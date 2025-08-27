import pytest
from botocore.exceptions import ClientError

from examples.rds.synchronous.rds_synchronous_repository import \
    RDSRepository
from src.moto_testkit import AutoMotoTestKit


def _create_repo(mtk: AutoMotoTestKit) -> RDSRepository:
    """Cria instância de RDSRepository já conectada ao SQLite em memória."""
    repo = RDSRepository(endpoint_url=mtk.get_client("rds").meta.endpoint_url)
    repo.connect_db_sqlite()
    return repo


def test_create_and_list_rds() -> None:
    with AutoMotoTestKit(auto_start=True) as mtk:
        repo = _create_repo(mtk)
        created = repo.create_instance(
            db_instance_identifier="testdb",
            engine="postgres",
            db_instance_class="db.t3.micro",
            master_username="postgres",
            master_user_password="secret123!",
            allocated_storage=20,
            publicly_accessible=False,
            wait=False,
        )
        assert created["DBInstanceIdentifier"] == "testdb"
        assert any(i["DBInstanceIdentifier"] == "testdb" for i in repo.list_instances())


def test_delete_rds_instance() -> None:
    with AutoMotoTestKit(auto_start=True) as mtk:
        repo = _create_repo(mtk)
        repo.create_instance(
            db_instance_identifier="testdb",
            engine="postgres",
            db_instance_class="db.t3.micro",
            master_username="postgres",
            master_user_password="secret123!",
            allocated_storage=20,
            publicly_accessible=False,
            wait=False,
        )
        deleted = repo.delete_instance(db_instance_identifier="testdb")
        assert deleted["DBInstanceIdentifier"] == "testdb"


def test_describe_instance() -> None:
    with AutoMotoTestKit(auto_start=True) as mtk:
        repo = _create_repo(mtk)
        repo.create_instance(
            db_instance_identifier="descdb",
            engine="postgres",
            db_instance_class="db.t3.micro",
            master_username="postgres",
            master_user_password="secret123!",
            allocated_storage=20,
            wait=False,
        )
        desc = repo.describe_instance("descdb")
        assert desc is not None
        assert desc["DBInstanceIdentifier"] == "descdb"


def test_list_instances_empty() -> None:
    with AutoMotoTestKit(auto_start=True) as mtk:
        repo = _create_repo(mtk)
        assert repo.list_instances() == []


def test_create_multiple_instances() -> None:
    with AutoMotoTestKit(auto_start=True) as mtk:
        repo = _create_repo(mtk)
        ids = ["db1", "db2", "db3"]
        for db_id in ids:
            repo.create_instance(
                db_instance_identifier=db_id,
                engine="postgres",
                db_instance_class="db.t3.micro",
                master_username="postgres",
                master_user_password="secret123!",
                allocated_storage=20,
                wait=False,
            )
        listed_ids = [i["DBInstanceIdentifier"] for i in repo.list_instances()]
        for db_id in ids:
            assert db_id in listed_ids


def test_delete_nonexistent_instance() -> None:
    with AutoMotoTestKit(auto_start=True) as mtk:
        repo = _create_repo(mtk)
        with pytest.raises(ClientError):
            repo.delete_instance(db_instance_identifier="no-such-db")


def test_create_instance_with_tags() -> None:
    with AutoMotoTestKit(auto_start=True) as mtk:
        repo = _create_repo(mtk)
        tags = {"env": "dev", "owner": "qa-team"}
        created = repo.create_instance(
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
        assert tag_dict == tags


def test_sqlite_create_insert_fetch() -> None:
    with AutoMotoTestKit(auto_start=True) as mtk:
        repo = _create_repo(mtk)
        repo.create_table_sql("users", "id INTEGER PRIMARY KEY, name TEXT, email TEXT")
        repo.insert_record("users", ["name", "email"], ("Alice", "alice@example.com"))
        repo.insert_record("users", ["name", "email"], ("Bob", "bob@example.com"))
        rows = repo.fetch_all("users")
        assert len(rows) == 2
        assert rows[0]["name"] == "Alice"
        assert rows[1]["name"] == "Bob"
