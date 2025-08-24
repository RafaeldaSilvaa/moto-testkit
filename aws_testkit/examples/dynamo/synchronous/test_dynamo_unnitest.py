# test_dynamo_unittest.py
import unittest
from aws_testkit.src.moto_testkit import use_moto_testkit
from dynamodb_synchronous_repository import DynamoDBRepository


class TestDynamoDBRepository(unittest.TestCase):
    # Usamos o decorador aqui, onde a mágica de setup e teardown acontece
    @classmethod
    @use_moto_testkit(auto_start=True)
    def setUpClass(cls, moto_testkit):
        """
        Este método agora recebe a instância moto_testkit injetada pelo decorador.
        O ambiente Moto será iniciado aqui e permanecerá ativo durante a execução
        de todos os métodos de teste.
        """
        # Salva a instância no 'self' da classe para que outros métodos a usem
        cls.moto_testkit = moto_testkit
        dynamodb_client = cls.moto_testkit.get_client("dynamodb")

        # A URL do endpoint é crucial para o Boto3 se conectar ao Moto
        cls.repo = DynamoDBRepository(
            endpoint_url=dynamodb_client.meta.endpoint_url
        )

        # A tabela é criada uma única vez no setup da classe
        cls.repo.create_table(
            table_name="Users",
            key_schema=[{"AttributeName": "id", "KeyType": "HASH"}],
            attribute_definitions=[{"AttributeName": "id", "AttributeType": "S"}],
            provisioned_throughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
        )

    # Os métodos de teste não precisam mais do decorador
    # Eles simplesmente usam a instância e a tabela que foram criadas em setUpClass
    def test_put_and_get_item(self):
        self.repo.put_item("Users", {"id": {"S": "1"}, "name": {"S": "Alice"}})
        item = self.repo.get_item("Users", {"id": {"S": "1"}})
        self.assertEqual(item["name"]["S"], "Alice")

    def test_query_items(self):
        self.repo.put_item("Users", {"id": {"S": "1"}, "name": {"S": "Alice"}})
        items = self.repo.query_items(
            "Users",
            "id = :id",
            {":id": {"S": "1"}}
        )
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["name"]["S"], "Alice")

    # O teardown não é estritamente necessário porque o decorador lida com a limpeza,
    # mas é boa prática ter um para fechar os clientes, se necessário.
    def tearDown(self):
        # A instância moto_testkit ainda está acessível aqui, se você precisar fazer algo
        # self.moto_testkit.clients.close_clients()
        pass