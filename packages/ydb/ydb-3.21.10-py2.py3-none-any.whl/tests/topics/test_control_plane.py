import os.path

import pytest

import ydb
from ydb import issues


@pytest.mark.asyncio
class TestTopicClientControlPlaneAsyncIO:
    async def test_create_topic(self, driver, database):
        client = driver.topic_client

        topic_path = database + "/my-test-topic"

        await client.create_topic(topic_path)

        with pytest.raises(issues.SchemeError):
            # double create is ok - try create topic with bad path
            await client.create_topic(database)

    async def test_drop_topic(self, driver, topic_path):
        client = driver.topic_client

        await client.drop_topic(topic_path)

        with pytest.raises(issues.SchemeError):
            await client.drop_topic(topic_path)

    async def test_describe_topic(self, driver, topic_path: str, topic_consumer):
        res = await driver.topic_client.describe_topic(topic_path)

        assert res.self.name == os.path.basename(topic_path)

        has_consumer = False
        for consumer in res.consumers:
            assert consumer.consumer_stats is not None
            for stat in ["min_partitions_last_read_time", "max_read_time_lag", "max_write_time_lag", "bytes_read"]:
                assert getattr(consumer.consumer_stats, stat, None) is not None
            if consumer.name == topic_consumer:
                has_consumer = True
                break

        assert has_consumer

    async def test_alter_not_existed_topic(self, driver, topic_path):
        client = driver.topic_client

        with pytest.raises(issues.SchemeError):
            await client.alter_topic(topic_path + "-not-exist")

    async def test_alter_existed_topic(self, driver, topic_path):
        client = driver.topic_client

        topic_before = await client.describe_topic(topic_path)

        target_min_active_partitions = topic_before.min_active_partitions + 1
        await client.alter_topic(topic_path, set_min_active_partitions=target_min_active_partitions)

        topic_after = await client.describe_topic(topic_path)
        assert topic_after.min_active_partitions == target_min_active_partitions

    async def test_alter_auto_partitioning_settings(self, driver, topic_path):
        client = driver.topic_client

        topic_before = await client.describe_topic(topic_path)

        expected = topic_before.auto_partitioning_settings

        expected.strategy = ydb.TopicAutoPartitioningStrategy.SCALE_UP

        await client.alter_topic(
            topic_path,
            alter_auto_partitioning_settings=ydb.TopicAlterAutoPartitioningSettings(
                set_strategy=ydb.TopicAutoPartitioningStrategy.SCALE_UP,
            ),
        )

        topic_after = await client.describe_topic(topic_path)

        assert topic_after.auto_partitioning_settings == expected

        expected.up_utilization_percent = 88

        await client.alter_topic(
            topic_path,
            alter_auto_partitioning_settings=ydb.TopicAlterAutoPartitioningSettings(
                set_up_utilization_percent=88,
            ),
        )

        topic_after = await client.describe_topic(topic_path)

        assert topic_after.auto_partitioning_settings == expected


class TestTopicClientControlPlane:
    def test_create_topic(self, driver_sync, database):
        client = driver_sync.topic_client

        topic_path = database + "/my-test-topic"

        client.create_topic(topic_path)

        with pytest.raises(issues.SchemeError):
            # double create is ok - try create topic with bad path
            client.create_topic(database)

    def test_drop_topic(self, driver_sync, topic_path):
        client = driver_sync.topic_client

        client.drop_topic(topic_path)

        with pytest.raises(issues.SchemeError):
            client.drop_topic(topic_path)

    def test_describe_topic(self, driver_sync, topic_path: str, topic_consumer):
        res = driver_sync.topic_client.describe_topic(topic_path)

        assert res.self.name == os.path.basename(topic_path)

        has_consumer = False
        for consumer in res.consumers:
            if consumer.name == topic_consumer:
                has_consumer = True
                break

        assert has_consumer

    def test_alter_not_existed_topic(self, driver_sync, topic_path):
        client = driver_sync.topic_client

        with pytest.raises(issues.SchemeError):
            client.alter_topic(topic_path + "-not-exist")

    def test_alter_existed_topic(self, driver_sync, topic_path):
        client = driver_sync.topic_client

        topic_before = client.describe_topic(topic_path)

        target_min_active_partitions = topic_before.min_active_partitions + 1
        client.alter_topic(topic_path, set_min_active_partitions=target_min_active_partitions)

        topic_after = client.describe_topic(topic_path)
        assert topic_after.min_active_partitions == target_min_active_partitions
