from aws_testkit.examples.sns.synchronous.sns_synchronous_repository import SNSRepository
from aws_testkit.src.moto_testkit import AutoMotoTestKit, use_moto_testkit


@use_moto_testkit(auto_start=True)
def test_create_and_list_topics_with_decorator(moto_testkit: AutoMotoTestKit) -> None:
    repository = SNSRepository(endpoint_url=moto_testkit.get_client("sns").meta.endpoint_url)
    arn = repository.create_topic("my-topic")
    assert "my-topic" in arn
    assert arn in repository.list_topics()


@use_moto_testkit(auto_start=True)
def test_publish_message_with_decorator(moto_testkit: AutoMotoTestKit) -> None:
    repository = SNSRepository(endpoint_url=moto_testkit.get_client("sns").meta.endpoint_url)
    arn = repository.create_topic("my-topic")
    resp = repository.publish(arn, "Hello SNS")
    assert "MessageId" in resp
