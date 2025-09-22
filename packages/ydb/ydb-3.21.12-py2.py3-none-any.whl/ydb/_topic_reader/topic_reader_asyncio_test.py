import asyncio
import concurrent.futures
import copy
import datetime
import gzip
import typing
from collections import OrderedDict
from dataclasses import dataclass
from unittest import mock

import pytest

from ydb import issues
from . import datatypes, topic_reader_asyncio
from .datatypes import PublicBatch, PublicMessage
from .topic_reader import PublicReaderSettings
from .topic_reader_asyncio import ReaderStream, ReaderReconnector, TopicReaderError
from .._grpc.grpcwrapper.common_utils import SupportedDriverType, ServerStatus
from .._grpc.grpcwrapper.ydb_topic import (
    StreamReadMessage,
    Codec,
    OffsetsRange,
    UpdateTokenRequest,
    UpdateTokenResponse,
)
from .._topic_common.test_helpers import (
    StreamMock,
    wait_condition,
    wait_for_fast,
    WaitConditionError,
)

# Workaround for good IDE and universal for runtime
if typing.TYPE_CHECKING:
    from .._grpc.v4.protos import ydb_status_codes_pb2
else:
    from .._grpc.common.protos import ydb_status_codes_pb2

from .._constants import DEFAULT_INITIAL_RESPONSE_TIMEOUT


@pytest.fixture(autouse=True)
def handle_exceptions(event_loop):
    def handler(loop, context):
        print(context)

    event_loop.set_exception_handler(handler)


@pytest.fixture()
def default_executor():
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=2, thread_name_prefix="decoder_executor")
    yield executor
    executor.shutdown()


def stub_partition_session(id: int = 0, ended: bool = False):
    partition_session = datatypes.PartitionSession(
        id=id,
        state=datatypes.PartitionSession.State.Active,
        topic_path="asd",
        partition_id=1,
        committed_offset=0,
        reader_reconnector_id=415,
        reader_stream_id=513,
    )

    if ended:
        partition_session.end()

    return partition_session


def stub_message(id: int):
    return PublicMessage(
        seqno=id,
        created_at=datetime.datetime(2023, 3, 18, 14, 15),
        message_group_id="",
        session_metadata={},
        offset=0,
        written_at=datetime.datetime(2023, 3, 18, 14, 15),
        producer_id="",
        data=id,
        metadata_items={},
        _partition_session=stub_partition_session(),
        _commit_start_offset=0,
        _commit_end_offset=1,
    )


@pytest.fixture()
def default_reader_settings(default_executor):
    return PublicReaderSettings(
        consumer="test-consumer",
        topic="test-topic",
        decoder_executor=default_executor,
    )


class StreamMockForReader(StreamMock):
    async def receive(self) -> StreamReadMessage.FromServer:
        return await super(self).receive()

    def write(self, message: StreamReadMessage.FromClient):
        return super().write(message)


@pytest.mark.asyncio
class TestReaderStream:
    default_batch_size = 1
    partition_session_id = 2
    partition_session_committed_offset = 10
    second_partition_session_id = 12
    second_partition_session_offset = 50
    default_reader_reconnector_id = 4

    @pytest.fixture()
    def stream(self):
        return StreamMock()

    @pytest.fixture()
    def partition_session(
        self, default_reader_settings, stream_reader_started: ReaderStream
    ) -> datatypes.PartitionSession:
        partition_session = datatypes.PartitionSession(
            id=2,
            topic_path=default_reader_settings.topic,
            partition_id=4,
            state=datatypes.PartitionSession.State.Active,
            committed_offset=self.partition_session_committed_offset,
            reader_reconnector_id=self.default_reader_reconnector_id,
            reader_stream_id=stream_reader_started._id,
        )

        assert partition_session.id not in stream_reader_started._partition_sessions
        stream_reader_started._partition_sessions[partition_session.id] = partition_session

        return stream_reader_started._partition_sessions[partition_session.id]

    @pytest.fixture()
    def second_partition_session(self, default_reader_settings, stream_reader_started: ReaderStream):
        partition_session = datatypes.PartitionSession(
            id=12,
            topic_path=default_reader_settings.topic,
            partition_id=10,
            state=datatypes.PartitionSession.State.Active,
            committed_offset=self.second_partition_session_offset,
            reader_reconnector_id=self.default_reader_reconnector_id,
            reader_stream_id=stream_reader_started._id,
        )

        assert partition_session.id not in stream_reader_started._partition_sessions
        stream_reader_started._partition_sessions[partition_session.id] = partition_session

        return stream_reader_started._partition_sessions[partition_session.id]

    async def get_started_reader(self, stream, *args, **kwargs) -> ReaderStream:
        reader = ReaderStream(self.default_reader_reconnector_id, *args, **kwargs)
        init_message = object()

        # noinspection PyTypeChecker
        start = asyncio.create_task(reader._start(stream, init_message))

        stream.from_server.put_nowait(
            StreamReadMessage.FromServer(
                server_status=ServerStatus(ydb_status_codes_pb2.StatusIds.SUCCESS, []),
                server_message=StreamReadMessage.InitResponse(session_id="test-session"),
            )
        )

        init_request = await wait_for_fast(stream.from_client.get())
        assert init_request.client_message == init_message

        read_request = await wait_for_fast(stream.from_client.get())
        assert isinstance(read_request.client_message, StreamReadMessage.ReadRequest)

        await start

        await asyncio.sleep(0)
        with pytest.raises(asyncio.QueueEmpty):
            stream.from_client.get_nowait()

        return reader

    @pytest.fixture()
    async def stream_reader_started(self, stream, default_reader_settings) -> ReaderStream:
        return await self.get_started_reader(stream, default_reader_settings)

    @pytest.fixture()
    async def stream_reader(self, stream_reader_started: ReaderStream):
        yield stream_reader_started

        assert stream_reader_started._get_first_error() is None
        await stream_reader_started.close(False)

    @pytest.fixture()
    async def stream_reader_finish_with_error(self, stream_reader_started: ReaderStream):
        yield stream_reader_started

        assert stream_reader_started._get_first_error() is not None
        await stream_reader_started.close(False)

    @staticmethod
    def create_message(
        partition_session: typing.Optional[datatypes.PartitionSession],
        seqno: int,
        offset_delta: int,
    ):
        return PublicMessage(
            seqno=seqno,
            created_at=datetime.datetime(2023, 2, 3, 14, 15),
            message_group_id="test-message-group",
            session_metadata={},
            offset=partition_session._next_message_start_commit_offset + offset_delta - 1,
            written_at=datetime.datetime(2023, 2, 3, 14, 16),
            producer_id="test-producer-id",
            data=bytes(),
            metadata_items={},
            _partition_session=partition_session,
            _commit_start_offset=partition_session._next_message_start_commit_offset + offset_delta - 1,
            _commit_end_offset=partition_session._next_message_start_commit_offset + offset_delta,
        )

    async def send_message(self, stream_reader, message: PublicMessage, new_batch=True):
        await self.send_batch(stream_reader, [message], new_batch=new_batch)

    async def send_batch(self, stream_reader, batch: typing.List[PublicMessage], new_batch=True):
        if len(batch) == 0:
            return

        first_message = batch[0]
        for message in batch:
            assert message._partition_session is first_message._partition_session

        partition_session_id = first_message._partition_session.id

        def batch_count():
            return len(stream_reader._message_batches)

        def batch_size():
            return len(stream_reader._message_batches[partition_session_id].messages)

        initial_batches = batch_count()
        initial_batch_size = 0 if new_batch else batch_size()

        stream = stream_reader._stream  # type: StreamMock
        stream.from_server.put_nowait(
            StreamReadMessage.FromServer(
                server_status=ServerStatus(ydb_status_codes_pb2.StatusIds.SUCCESS, []),
                server_message=StreamReadMessage.ReadResponse(
                    partition_data=[
                        StreamReadMessage.ReadResponse.PartitionData(
                            partition_session_id=first_message._partition_session.id,
                            batches=[
                                StreamReadMessage.ReadResponse.Batch(
                                    message_data=[
                                        StreamReadMessage.ReadResponse.MessageData(
                                            offset=message.offset,
                                            seq_no=message.seqno,
                                            created_at=message.created_at,
                                            data=message.data,
                                            metadata_items={},
                                            uncompresed_size=len(message.data),
                                            message_group_id=message.message_group_id,
                                        )
                                        for message in batch
                                    ],
                                    producer_id=first_message.producer_id,
                                    write_session_meta=first_message.session_metadata,
                                    codec=Codec.CODEC_RAW,
                                    written_at=first_message.written_at,
                                )
                            ],
                        )
                    ],
                    bytes_size=self.default_batch_size,
                ),
            )
        )
        if new_batch:
            await wait_condition(lambda: batch_count() > initial_batches)
        else:
            await wait_condition(lambda: batch_size() > initial_batch_size)

    async def test_unknown_error(self, stream, stream_reader_finish_with_error):
        class TestError(Exception):
            pass

        test_err = TestError()
        stream.from_server.put_nowait(test_err)

        with pytest.raises(TestError):
            await wait_for_fast(stream_reader_finish_with_error.wait_messages())

        with pytest.raises(TestError):
            stream_reader_finish_with_error.receive_batch_nowait()

    @pytest.mark.parametrize(
        "commit,send_range",
        [
            (
                OffsetsRange(
                    partition_session_committed_offset,
                    partition_session_committed_offset + 1,
                ),
                True,
            ),
            (
                OffsetsRange(
                    partition_session_committed_offset - 1,
                    partition_session_committed_offset,
                ),
                False,
            ),
        ],
    )
    async def test_send_commit_messages(
        self,
        stream,
        stream_reader: ReaderStream,
        partition_session,
        commit: OffsetsRange,
        send_range: bool,
    ):
        @dataclass
        class Commitable(datatypes.ICommittable):
            start: int
            end: int

            def _commit_get_partition_session(self) -> datatypes.PartitionSession:
                return partition_session

            def _commit_get_offsets_range(self) -> OffsetsRange:
                return OffsetsRange(self.start, self.end)

        start_ack_waiters = partition_session._ack_waiters.copy()

        waiter = stream_reader.commit(Commitable(commit.start, commit.end))

        async def wait_message():
            return await wait_for_fast(stream.from_client.get(), timeout=0)

        if send_range:
            msg = await wait_message()  # type: StreamReadMessage.FromClient
            assert msg.client_message == StreamReadMessage.CommitOffsetRequest(
                commit_offsets=[
                    StreamReadMessage.CommitOffsetRequest.PartitionCommitOffset(
                        partition_session_id=partition_session.id,
                        offsets=[commit],
                    )
                ]
            )
            assert partition_session._ack_waiters[-1].end_offset == commit.end
        else:
            assert waiter.future.done()

            with pytest.raises(WaitConditionError):
                msg = await wait_message()
                pass
            assert start_ack_waiters == partition_session._ack_waiters

    async def test_commit_ack_received(self, stream_reader, stream, partition_session, second_partition_session):
        offset1 = self.partition_session_committed_offset + 1
        waiter1 = partition_session.add_waiter(offset1)

        offset2 = self.second_partition_session_offset + 2
        waiter2 = second_partition_session.add_waiter(offset2)

        stream.from_server.put_nowait(
            StreamReadMessage.FromServer(
                server_status=ServerStatus(ydb_status_codes_pb2.StatusIds.SUCCESS, []),
                server_message=StreamReadMessage.CommitOffsetResponse(
                    partitions_committed_offsets=[
                        StreamReadMessage.CommitOffsetResponse.PartitionCommittedOffset(
                            partition_session_id=partition_session.id,
                            committed_offset=offset1,
                        ),
                        StreamReadMessage.CommitOffsetResponse.PartitionCommittedOffset(
                            partition_session_id=second_partition_session.id,
                            committed_offset=offset2,
                        ),
                    ]
                ),
            )
        )

        await wait_for_fast(waiter1.future)
        await wait_for_fast(waiter2.future)

    async def test_close_ack_waiters_when_close_stream_reader(
        self, stream_reader_started: ReaderStream, partition_session
    ):
        waiter = partition_session.add_waiter(self.partition_session_committed_offset + 1)
        await wait_for_fast(stream_reader_started.close(False))

        with pytest.raises(topic_reader_asyncio.PublicTopicReaderPartitionExpiredError):
            waiter.future.result()

    async def test_flush(self, stream, stream_reader_started: ReaderStream, partition_session):
        offset = self.partition_session_committed_offset + 1
        waiter = partition_session.add_waiter(offset)

        with pytest.raises(WaitConditionError):
            await wait_for_fast(stream_reader_started.flush(), timeout=0.1)

        stream.from_server.put_nowait(
            StreamReadMessage.FromServer(
                server_status=ServerStatus(ydb_status_codes_pb2.StatusIds.SUCCESS, []),
                server_message=StreamReadMessage.CommitOffsetResponse(
                    partitions_committed_offsets=[
                        StreamReadMessage.CommitOffsetResponse.PartitionCommittedOffset(
                            partition_session_id=partition_session.id,
                            committed_offset=offset,
                        ),
                    ]
                ),
            )
        )

        await stream_reader_started.flush()
        # don't raises
        assert waiter.future.result() is None

        await wait_for_fast(stream_reader_started.close(False))

    async def test_commit_ranges_for_received_messages(
        self, stream, stream_reader_started: ReaderStream, partition_session
    ):
        m1 = self.create_message(partition_session, 1, 1)
        m2 = self.create_message(partition_session, 2, 10)
        m2._commit_start_offset = m1.offset + 1

        await self.send_message(stream_reader_started, m1)
        await self.send_message(stream_reader_started, m2, new_batch=False)

        await stream_reader_started.wait_messages()
        received = stream_reader_started.receive_batch_nowait().messages
        assert received == [m1, m2]

        await stream_reader_started.close(False)

    # noinspection PyTypeChecker
    @pytest.mark.parametrize(
        "batch,data_out",
        [
            (
                PublicBatch(
                    messages=[
                        PublicMessage(
                            seqno=1,
                            created_at=datetime.datetime(2023, 3, 14, 15, 41),
                            message_group_id="",
                            session_metadata={},
                            offset=1,
                            written_at=datetime.datetime(2023, 3, 14, 15, 42),
                            producer_id="asd",
                            data=rb"123",
                            metadata_items={},
                            _partition_session=None,
                            _commit_start_offset=5,
                            _commit_end_offset=15,
                        )
                    ],
                    _partition_session=None,
                    _bytes_size=0,
                    _codec=Codec.CODEC_RAW,
                ),
                [bytes(rb"123")],
            ),
            (
                PublicBatch(
                    messages=[
                        PublicMessage(
                            seqno=1,
                            created_at=datetime.datetime(2023, 3, 14, 15, 41),
                            message_group_id="",
                            session_metadata={},
                            offset=1,
                            written_at=datetime.datetime(2023, 3, 14, 15, 42),
                            producer_id="asd",
                            data=gzip.compress(rb"123"),
                            metadata_items={},
                            _partition_session=None,
                            _commit_start_offset=5,
                            _commit_end_offset=15,
                        )
                    ],
                    _partition_session=None,
                    _bytes_size=0,
                    _codec=Codec.CODEC_GZIP,
                ),
                [bytes(rb"123")],
            ),
            (
                PublicBatch(
                    messages=[
                        PublicMessage(
                            seqno=1,
                            created_at=datetime.datetime(2023, 3, 14, 15, 41),
                            message_group_id="",
                            session_metadata={},
                            offset=1,
                            written_at=datetime.datetime(2023, 3, 14, 15, 42),
                            producer_id="asd",
                            metadata_items={},
                            data=rb"123",
                            _partition_session=None,
                            _commit_start_offset=5,
                            _commit_end_offset=15,
                        ),
                        PublicMessage(
                            seqno=1,
                            created_at=datetime.datetime(2023, 3, 14, 15, 41),
                            message_group_id="",
                            session_metadata={},
                            offset=1,
                            written_at=datetime.datetime(2023, 3, 14, 15, 42),
                            producer_id="asd",
                            data=rb"456",
                            metadata_items={},
                            _partition_session=None,
                            _commit_start_offset=5,
                            _commit_end_offset=15,
                        ),
                    ],
                    _partition_session=None,
                    _bytes_size=0,
                    _codec=Codec.CODEC_RAW,
                ),
                [bytes(rb"123"), bytes(rb"456")],
            ),
            (
                PublicBatch(
                    messages=[
                        PublicMessage(
                            seqno=1,
                            created_at=datetime.datetime(2023, 3, 14, 15, 41),
                            message_group_id="",
                            session_metadata={},
                            offset=1,
                            written_at=datetime.datetime(2023, 3, 14, 15, 42),
                            producer_id="asd",
                            data=gzip.compress(rb"123"),
                            metadata_items={},
                            _partition_session=None,
                            _commit_start_offset=5,
                            _commit_end_offset=15,
                        ),
                        PublicMessage(
                            seqno=1,
                            created_at=datetime.datetime(2023, 3, 14, 15, 41),
                            message_group_id="",
                            session_metadata={},
                            offset=1,
                            written_at=datetime.datetime(2023, 3, 14, 15, 42),
                            producer_id="asd",
                            data=gzip.compress(rb"456"),
                            metadata_items={},
                            _partition_session=None,
                            _commit_start_offset=5,
                            _commit_end_offset=15,
                        ),
                    ],
                    _partition_session=None,
                    _bytes_size=0,
                    _codec=Codec.CODEC_GZIP,
                ),
                [bytes(rb"123"), bytes(rb"456")],
            ),
        ],
    )
    async def test_decode_loop(self, stream_reader, batch: PublicBatch, data_out: typing.List[bytes]):
        assert len(batch.messages) == len(data_out)

        expected = copy.deepcopy(batch)
        expected._codec = Codec.CODEC_RAW

        for index, data in enumerate(data_out):
            expected.messages[index].data = data

        await wait_for_fast(stream_reader._decode_batch_inplace(batch))

        assert batch == expected

    async def test_error_from_status_code(self, stream, stream_reader_finish_with_error):
        # noinspection PyTypeChecker
        stream.from_server.put_nowait(
            StreamReadMessage.FromServer(
                server_status=ServerStatus(
                    status=issues.StatusCode.OVERLOADED,
                    issues=[],
                ),
                server_message=None,
            )
        )

        with pytest.raises(issues.Overloaded):
            await wait_for_fast(stream_reader_finish_with_error.wait_messages())

        with pytest.raises(issues.Overloaded):
            stream_reader_finish_with_error.receive_batch_nowait()

    async def test_init_reader(self, stream, default_reader_settings):
        reader = ReaderStream(self.default_reader_reconnector_id, default_reader_settings)
        init_message = StreamReadMessage.InitRequest(
            consumer="test-consumer",
            topics_read_settings=[
                StreamReadMessage.InitRequest.TopicReadSettings(
                    path="/local/test-topic",
                    partition_ids=[],
                    max_lag=None,
                    read_from=None,
                )
            ],
            auto_partitioning_support=False,
        )
        start_task = asyncio.create_task(reader._start(stream, init_message))

        sent_message = await wait_for_fast(stream.from_client.get())
        expected_sent_init_message = StreamReadMessage.FromClient(client_message=init_message)
        assert sent_message == expected_sent_init_message

        stream.from_server.put_nowait(
            StreamReadMessage.FromServer(
                server_status=ServerStatus(ydb_status_codes_pb2.StatusIds.SUCCESS, []),
                server_message=StreamReadMessage.InitResponse(session_id="test"),
            )
        )

        await start_task

        read_request = await wait_for_fast(stream.from_client.get())
        assert read_request.client_message == StreamReadMessage.ReadRequest(
            bytes_size=default_reader_settings.buffer_size_bytes,
        )

        assert reader._session_id == "test"
        await reader.close(False)

    async def test_start_partition(
        self,
        stream_reader: ReaderStream,
        stream,
        default_reader_settings,
        partition_session,
    ):
        def session_count():
            return len(stream_reader._partition_sessions)

        initial_session_count = session_count()

        test_partition_id = partition_session.partition_id + 1
        test_partition_session_id = partition_session.id + 1
        test_topic_path = default_reader_settings.topic + "-asd"
        test_partition_committed_offset = 18

        stream.from_server.put_nowait(
            StreamReadMessage.FromServer(
                server_status=ServerStatus(ydb_status_codes_pb2.StatusIds.SUCCESS, []),
                server_message=StreamReadMessage.StartPartitionSessionRequest(
                    partition_session=StreamReadMessage.PartitionSession(
                        partition_session_id=test_partition_session_id,
                        path=test_topic_path,
                        partition_id=test_partition_id,
                    ),
                    committed_offset=test_partition_committed_offset,
                    partition_offsets=OffsetsRange(
                        start=0,
                        end=0,
                    ),
                ),
            ),
        )
        response = await wait_for_fast(stream.from_client.get())
        assert response == StreamReadMessage.FromClient(
            client_message=StreamReadMessage.StartPartitionSessionResponse(
                partition_session_id=test_partition_session_id,
                read_offset=None,
                commit_offset=None,
            )
        )

        assert len(stream_reader._partition_sessions) == initial_session_count + 1
        assert stream_reader._partition_sessions[test_partition_session_id] == datatypes.PartitionSession(
            id=test_partition_session_id,
            state=datatypes.PartitionSession.State.Active,
            topic_path=test_topic_path,
            partition_id=test_partition_id,
            committed_offset=test_partition_committed_offset,
            reader_reconnector_id=self.default_reader_reconnector_id,
            reader_stream_id=stream_reader._id,
        )

    async def test_partition_stop_force(self, stream, stream_reader, partition_session):
        def session_count():
            return len(stream_reader._partition_sessions)

        initial_session_count = session_count()

        stream.from_server.put_nowait(
            StreamReadMessage.FromServer(
                server_status=ServerStatus(ydb_status_codes_pb2.StatusIds.SUCCESS, []),
                server_message=StreamReadMessage.StopPartitionSessionRequest(
                    partition_session_id=partition_session.id,
                    graceful=False,
                    committed_offset=0,
                ),
            )
        )

        await asyncio.sleep(0)  # wait next loop
        with pytest.raises(asyncio.QueueEmpty):
            stream.from_client.get_nowait()

        assert session_count() == initial_session_count - 1
        assert partition_session.id not in stream_reader._partition_sessions

    async def test_partition_stop_graceful(self, stream, stream_reader, partition_session):
        def session_count():
            return len(stream_reader._partition_sessions)

        initial_session_count = session_count()

        stream.from_server.put_nowait(
            StreamReadMessage.FromServer(
                server_status=ServerStatus(ydb_status_codes_pb2.StatusIds.SUCCESS, []),
                server_message=StreamReadMessage.StopPartitionSessionRequest(
                    partition_session_id=partition_session.id,
                    graceful=True,
                    committed_offset=0,
                ),
            )
        )

        resp = await wait_for_fast(stream.from_client.get())  # type: StreamReadMessage.FromClient
        assert session_count() == initial_session_count - 1
        assert partition_session.id not in stream_reader._partition_sessions
        assert resp.client_message == StreamReadMessage.StopPartitionSessionResponse(
            partition_session_id=partition_session.id
        )

        stream.from_server.put_nowait(
            StreamReadMessage.FromServer(
                server_status=ServerStatus(ydb_status_codes_pb2.StatusIds.SUCCESS, []),
                server_message=StreamReadMessage.StopPartitionSessionRequest(
                    partition_session_id=partition_session.id,
                    graceful=False,
                    committed_offset=0,
                ),
            )
        )

        await asyncio.sleep(0)  # wait next loop
        with pytest.raises(asyncio.QueueEmpty):
            stream.from_client.get_nowait()

    async def test_end_partition_session(self, stream, stream_reader, partition_session):
        def session_count():
            return len(stream_reader._partition_sessions)

        initial_session_count = session_count()

        stream.from_server.put_nowait(
            StreamReadMessage.FromServer(
                server_status=ServerStatus(ydb_status_codes_pb2.StatusIds.SUCCESS, []),
                server_message=StreamReadMessage.EndPartitionSession(
                    partition_session_id=partition_session.id,
                    adjacent_partition_ids=[],
                    child_partition_ids=[20, 30],
                ),
            )
        )

        await asyncio.sleep(0)  # wait next loop
        with pytest.raises(asyncio.QueueEmpty):
            stream.from_client.get_nowait()

        assert session_count() == initial_session_count
        assert partition_session.id in stream_reader._partition_sessions
        assert partition_session.ended

    @pytest.mark.parametrize(
        "graceful",
        (
            [True],
            [False],
        ),
    )
    async def test_free_buffer_after_partition_stop(self, stream, stream_reader, partition_session, graceful):
        initial_buffer_size = stream_reader._buffer_size_bytes
        message_size = initial_buffer_size - 1

        t = datetime.datetime.now(datetime.timezone.utc)

        stream.from_server.put_nowait(
            StreamReadMessage.FromServer(
                server_status=ServerStatus(issues.StatusCode.SUCCESS, []),
                server_message=StreamReadMessage.ReadResponse(
                    bytes_size=message_size,
                    partition_data=[
                        StreamReadMessage.ReadResponse.PartitionData(
                            partition_session_id=partition_session.id,
                            batches=[
                                StreamReadMessage.ReadResponse.Batch(
                                    message_data=[
                                        StreamReadMessage.ReadResponse.MessageData(
                                            partition_session.committed_offset + 1,
                                            seq_no=123,
                                            created_at=t,
                                            data=bytes(),
                                            metadata_items={},
                                            uncompresed_size=message_size,
                                            message_group_id="test-message-group",
                                        )
                                    ],
                                    producer_id="asd",
                                    write_session_meta={},
                                    codec=Codec.CODEC_RAW,
                                    written_at=t,
                                )
                            ],
                        )
                    ],
                ),
            )
        )

        def message_received():
            return len(stream_reader._message_batches) > 0

        await wait_condition(message_received)

        assert stream_reader._buffer_size_bytes == initial_buffer_size - message_size

        stream.from_server.put_nowait(
            StreamReadMessage.FromServer(
                server_status=ServerStatus(issues.StatusCode.SUCCESS, []),
                server_message=StreamReadMessage.StopPartitionSessionRequest(
                    partition_session_id=partition_session.id,
                    graceful=graceful,
                    committed_offset=partition_session.committed_offset,
                ),
            )
        )

        await wait_condition(lambda: partition_session.closed)

        batch = stream_reader.receive_batch_nowait()
        assert not batch.alive
        assert stream_reader._buffer_size_bytes == initial_buffer_size

    async def test_receive_message_from_server(
        self,
        stream_reader,
        stream,
        partition_session: datatypes.PartitionSession,
        second_partition_session,
    ):
        def reader_batch_count():
            return len(stream_reader._message_batches)

        initial_buffer_size = stream_reader._buffer_size_bytes
        initial_batch_count = reader_batch_count()

        bytes_size = 10
        created_at = datetime.datetime(2020, 1, 1, 18, 12)
        written_at = datetime.datetime(2023, 2, 1, 18, 12)
        producer_id = "test-producer-id"
        data = "123".encode()
        session_meta = {"a": "b"}
        message_group_id = "test-message-group-id"

        expected_message_offset = partition_session.committed_offset

        stream.from_server.put_nowait(
            StreamReadMessage.FromServer(
                server_status=ServerStatus(ydb_status_codes_pb2.StatusIds.SUCCESS, []),
                server_message=StreamReadMessage.ReadResponse(
                    bytes_size=bytes_size,
                    partition_data=[
                        StreamReadMessage.ReadResponse.PartitionData(
                            partition_session_id=partition_session.id,
                            batches=[
                                StreamReadMessage.ReadResponse.Batch(
                                    message_data=[
                                        StreamReadMessage.ReadResponse.MessageData(
                                            offset=expected_message_offset,
                                            seq_no=2,
                                            created_at=created_at,
                                            data=data,
                                            uncompresed_size=len(data),
                                            metadata_items={},
                                            message_group_id=message_group_id,
                                        )
                                    ],
                                    producer_id=producer_id,
                                    write_session_meta=session_meta,
                                    codec=Codec.CODEC_RAW,
                                    written_at=written_at,
                                )
                            ],
                        )
                    ],
                ),
            )
        ),

        await wait_condition(lambda: reader_batch_count() == initial_batch_count + 1)

        assert stream_reader._buffer_size_bytes == initial_buffer_size - bytes_size

        _, last_batch = stream_reader._message_batches.popitem()
        assert last_batch == PublicBatch(
            messages=[
                PublicMessage(
                    seqno=2,
                    created_at=created_at,
                    message_group_id=message_group_id,
                    session_metadata=session_meta,
                    offset=expected_message_offset,
                    written_at=written_at,
                    producer_id=producer_id,
                    data=data,
                    metadata_items={},
                    _partition_session=partition_session,
                    _commit_start_offset=expected_message_offset,
                    _commit_end_offset=expected_message_offset + 1,
                )
            ],
            _partition_session=partition_session,
            _bytes_size=bytes_size,
            _codec=Codec.CODEC_RAW,
        )

    async def test_read_batches(self, stream_reader, partition_session, second_partition_session):
        created_at = datetime.datetime(2020, 2, 1, 18, 12)
        created_at2 = datetime.datetime(2020, 2, 2, 18, 12)
        created_at3 = datetime.datetime(2020, 2, 3, 18, 12)
        created_at4 = datetime.datetime(2020, 2, 4, 18, 12)
        written_at = datetime.datetime(2023, 3, 1, 18, 12)
        written_at2 = datetime.datetime(2023, 3, 2, 18, 12)
        producer_id = "test-producer-id"
        producer_id2 = "test-producer-id"
        data = "123".encode()
        data2 = "1235".encode()
        session_meta = {"a": "b"}
        session_meta2 = {"b": "c"}

        message_group_id = "test-message-group-id"
        message_group_id2 = "test-message-group-id-2"

        partition1_mess1_expected_offset = partition_session.committed_offset
        partition2_mess1_expected_offset = second_partition_session.committed_offset
        partition2_mess2_expected_offset = second_partition_session.committed_offset + 1
        partition2_mess3_expected_offset = second_partition_session.committed_offset + 2

        batches = stream_reader._read_response_to_batches(
            StreamReadMessage.ReadResponse(
                bytes_size=3,
                partition_data=[
                    StreamReadMessage.ReadResponse.PartitionData(
                        partition_session_id=partition_session.id,
                        batches=[
                            StreamReadMessage.ReadResponse.Batch(
                                message_data=[
                                    StreamReadMessage.ReadResponse.MessageData(
                                        offset=partition1_mess1_expected_offset,
                                        seq_no=3,
                                        created_at=created_at,
                                        data=data,
                                        metadata_items={},
                                        uncompresed_size=len(data),
                                        message_group_id=message_group_id,
                                    )
                                ],
                                producer_id=producer_id,
                                write_session_meta=session_meta,
                                codec=Codec.CODEC_RAW,
                                written_at=written_at,
                            )
                        ],
                    ),
                    StreamReadMessage.ReadResponse.PartitionData(
                        partition_session_id=second_partition_session.id,
                        batches=[
                            StreamReadMessage.ReadResponse.Batch(
                                message_data=[
                                    StreamReadMessage.ReadResponse.MessageData(
                                        offset=partition2_mess1_expected_offset,
                                        seq_no=2,
                                        created_at=created_at2,
                                        data=data,
                                        metadata_items={},
                                        uncompresed_size=len(data),
                                        message_group_id=message_group_id,
                                    )
                                ],
                                producer_id=producer_id,
                                write_session_meta=session_meta,
                                codec=Codec.CODEC_RAW,
                                written_at=written_at2,
                            ),
                            StreamReadMessage.ReadResponse.Batch(
                                message_data=[
                                    StreamReadMessage.ReadResponse.MessageData(
                                        offset=partition2_mess2_expected_offset,
                                        seq_no=3,
                                        created_at=created_at3,
                                        data=data2,
                                        metadata_items={},
                                        uncompresed_size=len(data2),
                                        message_group_id=message_group_id,
                                    ),
                                    StreamReadMessage.ReadResponse.MessageData(
                                        offset=partition2_mess3_expected_offset,
                                        seq_no=5,
                                        created_at=created_at4,
                                        data=data,
                                        metadata_items={},
                                        uncompresed_size=len(data),
                                        message_group_id=message_group_id2,
                                    ),
                                ],
                                producer_id=producer_id2,
                                write_session_meta=session_meta2,
                                codec=Codec.CODEC_RAW,
                                written_at=written_at2,
                            ),
                        ],
                    ),
                ],
            )
        )

        last0 = batches[0]
        last1 = batches[1]
        last2 = batches[2]

        assert last0 == PublicBatch(
            messages=[
                PublicMessage(
                    seqno=3,
                    created_at=created_at,
                    message_group_id=message_group_id,
                    session_metadata=session_meta,
                    offset=partition1_mess1_expected_offset,
                    written_at=written_at,
                    producer_id=producer_id,
                    data=data,
                    metadata_items={},
                    _partition_session=partition_session,
                    _commit_start_offset=partition1_mess1_expected_offset,
                    _commit_end_offset=partition1_mess1_expected_offset + 1,
                )
            ],
            _partition_session=partition_session,
            _bytes_size=1,
            _codec=Codec.CODEC_RAW,
        )
        assert last1 == PublicBatch(
            messages=[
                PublicMessage(
                    seqno=2,
                    created_at=created_at2,
                    message_group_id=message_group_id,
                    session_metadata=session_meta,
                    offset=partition2_mess1_expected_offset,
                    written_at=written_at2,
                    producer_id=producer_id,
                    data=data,
                    metadata_items={},
                    _partition_session=second_partition_session,
                    _commit_start_offset=partition2_mess1_expected_offset,
                    _commit_end_offset=partition2_mess1_expected_offset + 1,
                )
            ],
            _partition_session=second_partition_session,
            _bytes_size=1,
            _codec=Codec.CODEC_RAW,
        )
        assert last2 == PublicBatch(
            messages=[
                PublicMessage(
                    seqno=3,
                    created_at=created_at3,
                    message_group_id=message_group_id,
                    session_metadata=session_meta2,
                    offset=partition2_mess2_expected_offset,
                    written_at=written_at2,
                    producer_id=producer_id2,
                    data=data2,
                    metadata_items={},
                    _partition_session=second_partition_session,
                    _commit_start_offset=partition2_mess2_expected_offset,
                    _commit_end_offset=partition2_mess2_expected_offset + 1,
                ),
                PublicMessage(
                    seqno=5,
                    created_at=created_at4,
                    message_group_id=message_group_id2,
                    session_metadata=session_meta2,
                    offset=partition2_mess3_expected_offset,
                    written_at=written_at2,
                    producer_id=producer_id,
                    data=data,
                    metadata_items={},
                    _partition_session=second_partition_session,
                    _commit_start_offset=partition2_mess3_expected_offset,
                    _commit_end_offset=partition2_mess3_expected_offset + 1,
                ),
            ],
            _partition_session=second_partition_session,
            _bytes_size=1,
            _codec=Codec.CODEC_RAW,
        )

    @pytest.mark.parametrize(
        "batches_before,expected_message,batches_after",
        [
            ({}, None, {}),
            (
                {
                    0: PublicBatch(
                        messages=[stub_message(1)],
                        _partition_session=stub_partition_session(),
                        _bytes_size=0,
                        _codec=Codec.CODEC_RAW,
                    )
                },
                stub_message(1),
                {},
            ),
            (
                {
                    0: PublicBatch(
                        messages=[stub_message(1), stub_message(2)],
                        _partition_session=stub_partition_session(),
                        _bytes_size=0,
                        _codec=Codec.CODEC_RAW,
                    ),
                    1: PublicBatch(
                        messages=[stub_message(3), stub_message(4)],
                        _partition_session=stub_partition_session(1),
                        _bytes_size=0,
                        _codec=Codec.CODEC_RAW,
                    ),
                },
                stub_message(1),
                {
                    0: PublicBatch(
                        messages=[stub_message(2)],
                        _partition_session=stub_partition_session(),
                        _bytes_size=0,
                        _codec=Codec.CODEC_RAW,
                    ),
                    1: PublicBatch(
                        messages=[stub_message(3), stub_message(4)],
                        _partition_session=stub_partition_session(1),
                        _bytes_size=0,
                        _codec=Codec.CODEC_RAW,
                    ),
                },
            ),
            (
                {
                    0: PublicBatch(
                        messages=[stub_message(1)],
                        _partition_session=stub_partition_session(),
                        _bytes_size=0,
                        _codec=Codec.CODEC_RAW,
                    ),
                    1: PublicBatch(
                        messages=[stub_message(2), stub_message(3)],
                        _partition_session=stub_partition_session(1),
                        _bytes_size=0,
                        _codec=Codec.CODEC_RAW,
                    ),
                },
                stub_message(1),
                {
                    1: PublicBatch(
                        messages=[stub_message(2), stub_message(3)],
                        _partition_session=stub_partition_session(1),
                        _bytes_size=0,
                        _codec=Codec.CODEC_RAW,
                    )
                },
            ),
        ],
    )
    async def test_read_message(
        self,
        stream_reader,
        batches_before: typing.List[datatypes.PublicBatch],
        expected_message: PublicMessage,
        batches_after: typing.List[datatypes.PublicBatch],
    ):
        stream_reader._message_batches = OrderedDict(batches_before)
        mess = stream_reader.receive_message_nowait()

        assert mess == expected_message
        assert dict(stream_reader._message_batches) == batches_after

    @pytest.mark.parametrize(
        "batches,expected_order",
        [
            (
                {
                    0: PublicBatch(
                        messages=[stub_message(1)],
                        _partition_session=stub_partition_session(0, ended=True),
                        _bytes_size=0,
                        _codec=Codec.CODEC_RAW,
                    )
                },
                [1],
            ),
            (
                {
                    0: PublicBatch(
                        messages=[stub_message(1), stub_message(2)],
                        _partition_session=stub_partition_session(0, ended=True),
                        _bytes_size=0,
                        _codec=Codec.CODEC_RAW,
                    ),
                    1: PublicBatch(
                        messages=[stub_message(3), stub_message(4)],
                        _partition_session=stub_partition_session(1),
                        _bytes_size=0,
                        _codec=Codec.CODEC_RAW,
                    ),
                },
                [1, 2, 3, 4],
            ),
            (
                {
                    0: PublicBatch(
                        messages=[stub_message(1), stub_message(2)],
                        _partition_session=stub_partition_session(0),
                        _bytes_size=0,
                        _codec=Codec.CODEC_RAW,
                    ),
                    1: PublicBatch(
                        messages=[stub_message(3), stub_message(4)],
                        _partition_session=stub_partition_session(1, ended=True),
                        _bytes_size=0,
                        _codec=Codec.CODEC_RAW,
                    ),
                    2: PublicBatch(
                        messages=[stub_message(5)],
                        _partition_session=stub_partition_session(2),
                        _bytes_size=0,
                        _codec=Codec.CODEC_RAW,
                    ),
                },
                [1, 3, 4, 5, 2],
            ),
        ],
    )
    async def test_read_message_autosplit_order(
        self,
        stream_reader,
        batches: typing.Dict[int, datatypes.PublicBatch],
        expected_order: typing.List[int],
    ):
        stream_reader._message_batches = OrderedDict(batches)

        for id, batch in batches.items():
            ps = batch._partition_session
            stream_reader._partition_sessions[id] = ps

        result = []
        for _ in range(len(expected_order)):
            mess = stream_reader.receive_message_nowait()
            result.append(mess.data)

        assert result == expected_order
        assert stream_reader.receive_message_nowait() is None

    @pytest.mark.parametrize(
        "batches_before,max_messages,actual_messages,batches_after",
        [
            (
                {
                    0: PublicBatch(
                        messages=[stub_message(1)],
                        _partition_session=stub_partition_session(),
                        _bytes_size=4,
                        _codec=Codec.CODEC_RAW,
                    )
                },
                None,
                1,
                {},
            ),
            (
                {
                    0: PublicBatch(
                        messages=[stub_message(1), stub_message(2)],
                        _partition_session=stub_partition_session(),
                        _bytes_size=4,
                        _codec=Codec.CODEC_RAW,
                    ),
                    1: PublicBatch(
                        messages=[stub_message(3), stub_message(4)],
                        _partition_session=stub_partition_session(1),
                        _bytes_size=4,
                        _codec=Codec.CODEC_RAW,
                    ),
                },
                1,
                1,
                {
                    1: PublicBatch(
                        messages=[stub_message(3), stub_message(4)],
                        _partition_session=stub_partition_session(1),
                        _bytes_size=4,
                        _codec=Codec.CODEC_RAW,
                    ),
                    0: PublicBatch(
                        messages=[stub_message(2)],
                        _partition_session=stub_partition_session(),
                        _bytes_size=2,
                        _codec=Codec.CODEC_RAW,
                    ),
                },
            ),
            (
                {
                    0: PublicBatch(
                        messages=[stub_message(1)],
                        _partition_session=stub_partition_session(),
                        _bytes_size=4,
                        _codec=Codec.CODEC_RAW,
                    ),
                    1: PublicBatch(
                        messages=[stub_message(2), stub_message(3)],
                        _partition_session=stub_partition_session(1),
                        _bytes_size=4,
                        _codec=Codec.CODEC_RAW,
                    ),
                },
                100,
                1,
                {
                    1: PublicBatch(
                        messages=[stub_message(2), stub_message(3)],
                        _partition_session=stub_partition_session(1),
                        _bytes_size=4,
                        _codec=Codec.CODEC_RAW,
                    )
                },
            ),
        ],
    )
    async def test_read_batch_max_messages(
        self,
        stream_reader,
        batches_before: typing.List[datatypes.PublicBatch],
        max_messages: typing.Optional[int],
        actual_messages: int,
        batches_after: typing.List[datatypes.PublicBatch],
    ):
        stream_reader._message_batches = OrderedDict(batches_before)
        batch = stream_reader.receive_batch_nowait(max_messages=max_messages)

        assert len(batch.messages) == actual_messages
        assert stream_reader._message_batches == OrderedDict(batches_after)

    async def test_receive_batch_nowait(self, stream, stream_reader, partition_session):
        assert stream_reader.receive_batch_nowait() is None

        initial_buffer_size = stream_reader._buffer_size_bytes

        mess1 = self.create_message(partition_session, 1, 1)
        await self.send_message(stream_reader, mess1)

        mess2 = self.create_message(partition_session, 2, 1)
        await self.send_message(stream_reader, mess2, new_batch=False)

        assert stream_reader._buffer_size_bytes == initial_buffer_size - 2 * self.default_batch_size

        received = stream_reader.receive_batch_nowait()
        assert received == PublicBatch(
            messages=[mess1, mess2],
            _partition_session=mess1._partition_session,
            _bytes_size=self.default_batch_size * 2,
            _codec=Codec.CODEC_RAW,
        )

        assert stream_reader._buffer_size_bytes == initial_buffer_size

        assert (
            StreamReadMessage.ReadRequest(self.default_batch_size * 2) == stream.from_client.get_nowait().client_message
        )

        with pytest.raises(asyncio.QueueEmpty):
            stream.from_client.get_nowait()

    async def test_receive_message_nowait(self, stream, stream_reader, partition_session):
        assert stream_reader.receive_batch_nowait() is None

        initial_buffer_size = stream_reader._buffer_size_bytes

        await self.send_batch(
            stream_reader,
            [
                self.create_message(partition_session, 1, 1),
                self.create_message(partition_session, 2, 1),
            ],
        )
        await self.send_batch(
            stream_reader,
            [
                self.create_message(partition_session, 10, 1),
            ],
            new_batch=False,
        )

        assert stream_reader._buffer_size_bytes == initial_buffer_size - 2 * self.default_batch_size

        for expected_seqno in [1, 2, 10]:
            mess = stream_reader.receive_message_nowait()
            assert mess.seqno == expected_seqno

        assert stream_reader._buffer_size_bytes == initial_buffer_size

    async def test_update_token(self, stream):
        settings = PublicReaderSettings(
            consumer="test-consumer",
            topic="test-topic",
            update_token_interval=0.1,
        )
        reader = await self.get_started_reader(stream, settings, get_token_function=lambda: "foo-bar")

        assert stream.from_client.empty()

        expected = StreamReadMessage.FromClient(UpdateTokenRequest(token="foo-bar"))
        got = await wait_for_fast(stream.from_client.get())
        assert expected == got, "send update token request"

        await asyncio.sleep(0.2)
        assert stream.from_client.empty(), "no answer - no new update request"

        await stream.from_server.put(
            StreamReadMessage.FromServer(
                server_status=ServerStatus(ydb_status_codes_pb2.StatusIds.SUCCESS, []),
                server_message=UpdateTokenResponse(),
            )
        )

        got = await wait_for_fast(stream.from_client.get())
        assert expected == got

        await reader.close(False)

    async def test_read_unknown_message(self, stream, stream_reader, caplog):
        class TestMessage:
            pass

        # noinspection PyTypeChecker
        stream.from_server.put_nowait(
            StreamReadMessage.FromServer(
                server_status=ServerStatus(
                    status=issues.StatusCode.SUCCESS,
                    issues=[],
                ),
                server_message=TestMessage(),
            )
        )

        def logged():
            for rec in caplog.records:
                if TestMessage.__name__ in rec.message:
                    return True
            return False

        await wait_condition(logged)

    async def test_init_timeout_parameter(self, stream, default_reader_settings):
        """Test that ReaderStream._start calls stream.receive with timeout=10"""
        reader = ReaderStream(self.default_reader_reconnector_id, default_reader_settings)
        init_message = default_reader_settings._init_message()

        # Mock stream.receive to check if timeout is passed
        with mock.patch.object(stream, "receive") as mock_receive:
            mock_receive.return_value = StreamReadMessage.FromServer(
                server_status=ServerStatus(ydb_status_codes_pb2.StatusIds.SUCCESS, []),
                server_message=StreamReadMessage.InitResponse(session_id="test_session"),
            )

            await reader._start(stream, init_message)

            # Verify that receive was called with timeout
            mock_receive.assert_called_with(timeout=DEFAULT_INITIAL_RESPONSE_TIMEOUT)

        await reader.close(False)

    async def test_init_timeout_behavior(self, stream, default_reader_settings):
        """Test that ReaderStream._start raises TopicReaderError when receive times out"""
        reader = ReaderStream(self.default_reader_reconnector_id, default_reader_settings)
        init_message = default_reader_settings._init_message()

        # Mock stream.receive to directly raise TimeoutError when called with timeout
        async def timeout_receive(timeout=None):
            if timeout == DEFAULT_INITIAL_RESPONSE_TIMEOUT:
                raise asyncio.TimeoutError("Simulated timeout")
            return StreamReadMessage.FromServer(
                server_status=ServerStatus(ydb_status_codes_pb2.StatusIds.SUCCESS, []),
                server_message=StreamReadMessage.InitResponse(session_id="test_session"),
            )

        with mock.patch.object(stream, "receive", side_effect=timeout_receive):
            # Should raise TopicReaderError with timeout message
            with pytest.raises(TopicReaderError, match="Timeout waiting for init response"):
                await reader._start(stream, init_message)

        await reader.close(False)


@pytest.mark.asyncio
class TestReaderReconnector:
    async def test_reconnect_on_repeatable_error(self, monkeypatch):
        test_error = issues.Overloaded("test error")

        async def wait_error():
            raise test_error

        reader_stream_mock_with_error = mock.Mock(ReaderStream)
        reader_stream_mock_with_error._id = 0
        reader_stream_mock_with_error.wait_error = mock.AsyncMock(side_effect=wait_error)

        async def wait_messages_with_error():
            raise test_error

        reader_stream_mock_with_error.wait_messages = mock.AsyncMock(side_effect=wait_messages_with_error)

        async def wait_forever():
            f = asyncio.Future()
            await f

        reader_stream_with_messages = mock.Mock(ReaderStream)
        reader_stream_with_messages._id = 0
        reader_stream_with_messages.wait_error = mock.AsyncMock(side_effect=wait_forever)
        reader_stream_with_messages.wait_messages.return_value = None

        stream_index = 0

        async def stream_create(
            reader_reconnector_id: int,
            driver: SupportedDriverType,
            settings: PublicReaderSettings,
        ):
            nonlocal stream_index
            stream_index += 1
            if stream_index == 1:
                return reader_stream_mock_with_error
            elif stream_index == 2:
                return reader_stream_with_messages
            else:
                raise Exception("unexpected create stream")

        with mock.patch.object(ReaderStream, "create", stream_create):
            reconnector = ReaderReconnector(mock.Mock(), PublicReaderSettings("", ""))
            await wait_for_fast(reconnector.wait_message())

        reader_stream_mock_with_error.wait_error.assert_any_await()
        reader_stream_mock_with_error.wait_messages.assert_any_await()
