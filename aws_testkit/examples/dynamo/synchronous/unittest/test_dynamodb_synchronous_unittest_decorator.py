import unittest
import boto3
from aws_testkit.examples.dynamo.synchronous.dynamodb_synchronous_repository import DynamoDBRepository
from aws_testkit.src.moto_testkit import use_moto_testkit

def create_resources(repository: DynamoDBRepository):
    repository.create_table(
        table_name="Users",
        key_schema=[{"AttributeName": "id", "KeyType": "HASH"}],
        attribute_definitions=[{"AttributeName": "id", "AttributeType": "S"}],
        provisioned_throughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )

@use_moto_testkit(auto_start=True)
class TestDynamoDBRepositoryIsolated(unittest.TestCase):
    """
    Classe de teste onde cada teste é isolado.
    Um novo ambiente Moto e uma nova tabela são criados para cada método de teste.
    """


    def setUp(self, moto_testkit):
        """
        Este método é executado ANTES de cada teste.
        O decorador garante que um NOVO ambiente Moto seja iniciado para cada teste,
        o que nos permite criar a tabela para cada um.
        """
        dynamodb_client = boto3.client("dynamodb")

        self.repo = DynamoDBRepository(
            endpoint_url=dynamodb_client.meta.endpoint_url
        )

    def test_put_and_get_item(self, moto_testkit):
        """
        Testa a inserção e recuperação de um item.
        A tabela é criada e populada apenas neste teste.
        """
        create_resources(self.repo)
        self.repo.put_item("Users", {"id": {"S": "1"}, "name": {"S": "Alice"}})
        item = self.repo.get_item("Users", {"id": {"S": "1"}})
        self.assertEqual(item["name"]["S"], "Alice")


    def test_query_items(self, moto_testkit):
        """
        Testa a funcionalidade de busca (query)
        Este teste começa com uma tabela vazia, recém-criada.
        """
        create_resources(self.repo)
        self.repo.put_item("Users", {"id": {"S": "1"}, "name": {"S": "User1"}})
        self.repo.put_item("Users", {"id": {"S": "2"}, "name": {"S": "User2"}})

        items = self.repo.query_items(
            "Users",
            "id = :id",
            {":id": {"S": "2"}}
        )

        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["name"]["S"], "User2")