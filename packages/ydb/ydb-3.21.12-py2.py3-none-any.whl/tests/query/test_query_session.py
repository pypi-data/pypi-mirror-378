import json

import pytest
import threading
import time
from concurrent.futures import _base as b
from unittest import mock

from ydb import QuerySessionPool
from ydb.query.base import QueryStatsMode, QueryExplainResultFormat
from ydb.query.session import QuerySession


def _check_session_state_empty(session: QuerySession):
    assert session._state.session_id is None
    assert session._state.node_id is None
    assert not session._state.attached


def _check_session_state_full(session: QuerySession):
    assert session._state.session_id is not None
    assert session._state.node_id is not None
    assert session._state.attached


class TestQuerySession:
    def test_session_normal_lifecycle(self, session: QuerySession):
        _check_session_state_empty(session)

        session.create()
        _check_session_state_full(session)

        session.delete()
        _check_session_state_empty(session)

    def test_second_create_do_nothing(self, session: QuerySession):
        session.create()
        _check_session_state_full(session)

        session_id_before = session._state.session_id
        node_id_before = session._state.node_id

        session.create()
        _check_session_state_full(session)

        assert session._state.session_id == session_id_before
        assert session._state.node_id == node_id_before

    def test_second_delete_do_nothing(self, session: QuerySession):
        session.create()

        session.delete()
        session.delete()

    def test_delete_before_create_not_possible(self, session: QuerySession):
        with pytest.raises(RuntimeError):
            session.delete()

    def test_create_after_delete_not_possible(self, session: QuerySession):
        session.create()
        session.delete()
        with pytest.raises(RuntimeError):
            session.create()

    def test_transaction_before_create_raises(self, session: QuerySession):
        with pytest.raises(RuntimeError):
            session.transaction()

    def test_transaction_after_delete_raises(self, session: QuerySession):
        session.create()

        session.delete()

        with pytest.raises(RuntimeError):
            session.transaction()

    def test_transaction_after_create_not_raises(self, session: QuerySession):
        session.create()
        session.transaction()

    def test_execute_before_create_raises(self, session: QuerySession):
        with pytest.raises(RuntimeError):
            session.execute("select 1;")

    def test_execute_after_delete_raises(self, session: QuerySession):
        session.create()
        session.delete()
        with pytest.raises(RuntimeError):
            session.execute("select 1;")

    def test_basic_execute(self, session: QuerySession):
        session.create()
        it = session.execute("select 1;")
        result_sets = [result_set for result_set in it]

        assert len(result_sets) == 1
        assert len(result_sets[0].rows) == 1
        assert len(result_sets[0].columns) == 1
        assert list(result_sets[0].rows[0].values()) == [1]

    def test_two_results(self, session: QuerySession):
        session.create()
        res = []
        counter = 0

        with session.execute("select 1; select 2") as results:
            for result_set in results:
                counter += 1
                if len(result_set.rows) > 0:
                    res.append(list(result_set.rows[0].values()))

        assert res == [[1], [2]]
        assert counter == 2

    def test_thread_leaks(self, session: QuerySession):
        session.create()
        thread_names = [t.name for t in threading.enumerate()]
        assert "first response attach stream thread" not in thread_names
        assert "attach stream thread" in thread_names

    def test_first_resp_timeout(self, session: QuerySession):
        class FakeStream:
            def __iter__(self):
                return self

            def __next__(self):
                time.sleep(10)
                return 1

            def cancel(self):
                pass

        fake_stream = mock.Mock(spec=FakeStream)

        session._attach_call = mock.MagicMock(return_value=fake_stream)
        assert session._attach_call() == fake_stream

        session._create_call()
        with pytest.raises(b.TimeoutError):
            session._attach(0.1)

        fake_stream.cancel.assert_called()

        thread_names = [t.name for t in threading.enumerate()]
        assert "first response attach stream thread" not in thread_names
        assert "attach stream thread" not in thread_names

        _check_session_state_empty(session)

    @pytest.mark.parametrize(
        "stats_mode",
        [
            None,
            QueryStatsMode.UNSPECIFIED,
            QueryStatsMode.NONE,
            QueryStatsMode.BASIC,
            QueryStatsMode.FULL,
            QueryStatsMode.PROFILE,
        ],
    )
    def test_stats_mode(self, session: QuerySession, stats_mode: QueryStatsMode):
        session.create()

        for _ in session.execute("SELECT 1; SELECT 2; SELECT 3;", stats_mode=stats_mode):
            pass

        stats = session.last_query_stats

        if stats_mode in [None, QueryStatsMode.NONE, QueryStatsMode.UNSPECIFIED]:
            assert stats is None
            return

        assert stats is not None
        assert len(stats.query_phases) > 0

        if stats_mode != QueryStatsMode.BASIC:
            assert len(stats.query_plan) > 0
        else:
            assert stats.query_plan == ""

    def test_explain(self, pool: QuerySessionPool):
        pool.execute_with_retries("DROP TABLE IF EXISTS test_explain")
        pool.execute_with_retries("CREATE TABLE test_explain (id Int64, PRIMARY KEY (id))")
        try:
            plan_fullscan = ""
            plan_lookup = ""

            def callee(session: QuerySession):
                nonlocal plan_fullscan, plan_lookup

                plan = session.explain("SELECT * FROM test_explain", result_format=QueryExplainResultFormat.STR)
                isinstance(plan, str)
                assert "FullScan" in plan

                plan_fullscan = session.explain(
                    "SELECT * FROM test_explain", result_format=QueryExplainResultFormat.DICT
                )

                plan_lookup = session.explain(
                    "SELECT * FROM test_explain WHERE id = $id",
                    {"$id": 1},
                    result_format=QueryExplainResultFormat.DICT,
                )

            pool.retry_operation_sync(callee)

            plan_fulltext_string = json.dumps(plan_fullscan)
            assert "FullScan" in plan_fulltext_string

            plan_lookup_string = json.dumps(plan_lookup)
            assert "Lookup" in plan_lookup_string
        finally:
            pool.execute_with_retries("DROP TABLE test_explain")
