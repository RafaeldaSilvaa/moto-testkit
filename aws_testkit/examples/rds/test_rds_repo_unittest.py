import unittest
from botocore.exceptions import ClientError
from aws_testkit.examples.rds.rds_repository import RDSRepository
from aws_testkit.src import MotoTestKit


class TestRDSRepositoryWithMoto(unittest.TestCase):
    def setUp(self):
        self.kit = MotoTestKit(auto_start=True)
        self.repo = RDSRepository(endpoint_url=self.kit.get_client("rds").meta.endpoint_url)
        # Conecta a um banco SQLite em memória para testar métodos SQL
        self.repo.connect_db_sqlite()

    def tearDown(self):
        self.kit.stop()

    def test_create_and_list_rds(self):
        created = self.repo.create_instance(
            db_instance_identifier="testdb",
            engine="postgres",
            db_instance_class="db.t3.micro",
            master_username="postgres",
            master_user_password="secret123!",
            allocated_storage=20,
            publicly_accessible=False,
            wait=False
        )
        self.assertEqual(created["DBInstanceIdentifier"], "testdb")
        listed = self.repo.list_instances()
        self.assertTrue(any(i["DBInstanceIdentifier"] == "testdb" for i in listed))

    def test_delete_rds_instance(self):
        self.repo.create_instance(
            db_instance_identifier="testdb",
            engine="postgres",
            db_instance_class="db.t3.micro",
            master_username="postgres",
            master_user_password="secret123!",
            allocated_storage=20,
            publicly_accessible=False,
            wait=False
        )
        deleted = self.repo.delete_instance(db_instance_identifier="testdb")
        self.assertEqual(deleted["DBInstanceIdentifier"], "testdb")

    def test_describe_instance(self):
        self.repo.create_instance(
            db_instance_identifier="descdb",
            engine="postgres",
            db_instance_class="db.t3.micro",
            master_username="postgres",
            master_user_password="secret123!",
            allocated_storage=20,
            wait=False
        )
        desc = self.repo.describe_instance("descdb")
        self.assertIsNotNone(desc)
        self.assertEqual(desc["DBInstanceIdentifier"], "descdb")

    def test_list_instances_empty(self):
        listed = self.repo.list_instances()
        self.assertEqual(listed, [])

    def test_create_multiple_instances(self):
        ids = ["db1", "db2", "db3"]
        for db_id in ids:
            self.repo.create_instance(
                db_instance_identifier=db_id,
                engine="postgres",
                db_instance_class="db.t3.micro",
                master_username="postgres",
                master_user_password="secret123!",
                allocated_storage=20,
                wait=False
            )
        listed_ids = [i["DBInstanceIdentifier"] for i in self.repo.list_instances()]
        for db_id in ids:
            self.assertIn(db_id, listed_ids)

    def test_delete_nonexistent_instance(self):
        with self.assertRaises(ClientError):
            self.repo.delete_instance(db_instance_identifier="no-such-db")

    def test_create_instance_with_tags(self):
        tags = {"env": "dev", "owner": "qa-team"}
        created = self.repo.create_instance(
            db_instance_identifier="tagged-db",
            engine="postgres",
            db_instance_class="db.t3.micro",
            master_username="postgres",
            master_user_password="secret123!",
            allocated_storage=20,
            tags=tags,
            wait=False
        )
        self.assertIn("TagList", created)
        tag_dict = {t["Key"]: t["Value"] for t in created["TagList"]}
        self.assertEqual(tag_dict, tags)

    def test_sqlite_create_insert_fetch(self):
        # Criar tabela
        self.repo.create_table_sql(
            "users",
            "id INTEGER PRIMARY KEY, name TEXT, email TEXT"
        )

        # Inserir registros
        self.repo.insert_record("users", ["name", "email"], ("Alice", "alice@example.com"))
        self.repo.insert_record("users", ["name", "email"], ("Bob", "bob@example.com"))

        # Buscar registros
        rows = self.repo.fetch_all("users")
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["name"], "Alice")
        self.assertEqual(rows[1]["name"], "Bob")


if __name__ == "__main__":
    unittest.main()
