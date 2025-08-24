# test_dynamo_unittest_class_level.py
import unittest
import boto3
from aws_testkit.examples.dynamo.synchronous.dynamodb_synchronous_repository import DynamoDBRepository
from aws_testkit.src.moto_testkit import use_moto_testkit


@use_moto_testkit(auto_start=True)
class TestDynamoDBRepositoryClass(unittest.TestCase):
    """
    Classe de teste que usa o setUpClass para criar o ambiente e a tabela apenas uma vez.
    O método setUp é usado para limpar a tabela antes de cada teste.
    """

    @classmethod
    def setUpClass(cls, moto_testkit):
        """
        Executado UMA VEZ antes de todos os testes.
        Cria o ambiente Moto e a tabela 'Users'.
        """
        # A instância do moto_testkit é injetada aqui
        cls.moto_testkit = moto_testkit
        dynamodb_client = boto3.client("dynamodb")

        cls.repo = DynamoDBRepository(
            endpoint_url=dynamodb_client.meta.endpoint_url
        )

        # A tabela é criada APENAS UMA VEZ
        cls.repo.create_table(
            table_name="Users",
            key_schema=[{"AttributeName": "id", "KeyType": "HASH"}],
            attribute_definitions=[{"AttributeName": "id", "AttributeType": "S"}],
            provisioned_throughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
        )

    def setUp(self):
        """
        Executado ANTES de cada teste. Limpa a tabela para garantir o isolamento.
        """
        # Para cada teste, limpamos a tabela criada no setUpClass.
        # Isso garante que um teste não influencie o outro.
        try:
            items = self.repo.query_items(
                "Users",
                "id = :id",
                {":id": {"S": "1"}}
            )
            for item in items:
                self.repo.delete_item("Users", {"id": item["id"]})
        except Exception:
            pass # A tabela pode estar vazia

    def test_put_and_get_item(self, moto_testkit):
        """
        Testa a inserção e recuperação. A tabela já existe e está limpa.
        """
        self.repo.put_item("Users", {"id": {"S": "1"}, "name": {"S": "Alice"}})
        item = self.repo.get_item("Users", {"id": {"S": "1"}})
        self.assertEqual(item["name"]["S"], "Alice")

    def test_query_items(self, moto_testkit):
        """
        Testa a busca. A tabela já existe e está limpa.
        """
        self.repo.put_item("Users", {"id": {"S": "1"}, "name": {"S": "User1"}})
        self.repo.put_item("Users", {"id": {"S": "2"}, "name": {"S": "User2"}})

        items = self.repo.query_items(
            "Users",
            "id = :id",
            {":id": {"S": "2"}}
        )

        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["name"]["S"], "User2")