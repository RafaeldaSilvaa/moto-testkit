from examples.sns.synchronous.sns_synchronous_repository import \
    SNSRepository
from src.moto_testkit import AutoMotoTestKit


def test_create_and_list_topics_with_context_manager() -> None:
    with AutoMotoTestKit(auto_start=True) as moto_testkit:
        repository = SNSRepository(
            endpoint_url=moto_testkit.get_client("sns").meta.endpoint_url
        )
        arn = repository.create_topic("my-topic")
        assert "my-topic" in arn
        assert arn in repository.list_topics()


def test_publish_message_with_context_manager() -> None:
    with AutoMotoTestKit(auto_start=True) as moto_testkit:
        repository = SNSRepository(
            endpoint_url=moto_testkit.get_client("sns").meta.endpoint_url
        )
        arn = repository.create_topic("my-topic")
        resp = repository.publish(arn, "Hello SNS")
        assert "MessageId" in resp
