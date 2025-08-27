import unittest

from botocore.exceptions import ClientError

from examples.rds.synchronous.rds_synchronous_repository import RDSRepository
from src import MotoTestKit


class TestRDSRepositoryFixtureMotoTestKit(unittest.TestCase):
    def setUp(self) -> None:
        self.moto_testkit: MotoTestKit = MotoTestKit(auto_start=True)
        self.repository: RDSRepository = RDSRepository(
            endpoint_url=self.moto_testkit.get_client("rds").meta.endpoint_url
        )
        self.repository.connect_db_sqlite()

    def tearDown(self) -> None:
        self.moto_testkit.stop()

    def test_create_and_list_rds(self) -> None:
        created = self.repository.create_instance(
            db_instance_identifier="testdb",
            engine="postgres",
            db_instance_class="db.t3.micro",
            master_username="postgres",
            master_user_password="secret123!",
            allocated_storage=20,
            publicly_accessible=False,
            wait=False,
        )
        self.assertEqual(created["DBInstanceIdentifier"], "testdb")
        self.assertTrue(
            any(
                i["DBInstanceIdentifier"] == "testdb"
                for i in self.repository.list_instances()
            )
        )

    def test_delete_rds_instance(self) -> None:
        self.repository.create_instance(
            db_instance_identifier="testdb",
            engine="postgres",
            db_instance_class="db.t3.micro",
            master_username="postgres",
            master_user_password="secret123!",
            allocated_storage=20,
            publicly_accessible=False,
            wait=False,
        )
        deleted = self.repository.delete_instance(db_instance_identifier="testdb")
        self.assertEqual(deleted["DBInstanceIdentifier"], "testdb")

    def test_describe_instance(self) -> None:
        self.repository.create_instance(
            db_instance_identifier="descdb",
            engine="postgres",
            db_instance_class="db.t3.micro",
            master_username="postgres",
            master_user_password="secret123!",
            allocated_storage=20,
            wait=False,
        )
        desc = self.repository.describe_instance("descdb")
        self.assertIsNotNone(desc)
        self.assertEqual(desc["DBInstanceIdentifier"], "descdb")

    def test_list_instances_empty(self) -> None:
        self.assertEqual(self.repository.list_instances(), [])

    def test_create_multiple_instances(self) -> None:
        ids = ["db1", "db2", "db3"]
        for db_id in ids:
            self.repository.create_instance(
                db_instance_identifier=db_id,
                engine="postgres",
                db_instance_class="db.t3.micro",
                master_username="postgres",
                master_user_password="secret123!",
                allocated_storage=20,
                wait=False,
            )
        listed_ids = [
            i["DBInstanceIdentifier"] for i in self.repository.list_instances()
        ]
        for db_id in ids:
            self.assertIn(db_id, listed_ids)

    def test_delete_nonexistent_instance(self) -> None:
        with self.assertRaises(ClientError):
            self.repository.delete_instance(db_instance_identifier="no-such-db")

    def test_create_instance_with_tags(self) -> None:
        tags = {"env": "dev", "owner": "qa-team"}
        created = self.repository.create_instance(
            db_instance_identifier="tagged-db",
            engine="postgres",
            db_instance_class="db.t3.micro",
            master_username="postgres",
            master_user_password="secret123!",
            allocated_storage=20,
            tags=tags,
            wait=False,
        )
        tag_dict = {t["Key"]: t["Value"] for t in created["TagList"]}
        self.assertEqual(tag_dict, tags)

    def test_sqlite_create_insert_fetch(self) -> None:
        self.repository.create_table_sql(
            "users", "id INTEGER PRIMARY KEY, name TEXT, email TEXT"
        )
        self.repository.insert_record(
            "users", ["name", "email"], ("Alice", "alice@example.com")
        )
        self.repository.insert_record(
            "users", ["name", "email"], ("Bob", "bob@example.com")
        )
        rows = self.repository.fetch_all("users")
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["name"], "Alice")
        self.assertEqual(rows[1]["name"], "Bob")
