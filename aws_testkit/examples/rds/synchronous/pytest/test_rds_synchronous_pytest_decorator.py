import pytest
from botocore.exceptions import ClientError

from aws_testkit.examples.rds.synchronous.rds_synchronous_repository import RDSRepository
from aws_testkit.src.moto_testkit import AutoMotoTestKit, use_moto_testkit


def _create_repo(moto_testkit: AutoMotoTestKit) -> RDSRepository:
    """Cria uma instância de RDSRepository já conectada ao SQLite em memória."""
    repo = RDSRepository(endpoint_url=moto_testkit.get_client("rds").meta.endpoint_url)
    repo.connect_db_sqlite()
    return repo


@use_moto_testkit(auto_start=True)
def test_create_and_list_rds(moto_testkit: AutoMotoTestKit) -> None:
    repo = _create_repo(moto_testkit)
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


@use_moto_testkit(auto_start=True)
def test_delete_rds_instance(moto_testkit: AutoMotoTestKit) -> None:
    repo = _create_repo(moto_testkit)
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


@use_moto_testkit(auto_start=True)
def test_describe_instance(moto_testkit: AutoMotoTestKit) -> None:
    repo = _create_repo(moto_testkit)
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


@use_moto_testkit(auto_start=True)
def test_list_instances_empty(moto_testkit: AutoMotoTestKit) -> None:
    repo = _create_repo(moto_testkit)
    assert repo.list_instances() == []


@use_moto_testkit(auto_start=True)
def test_create_multiple_instances(moto_testkit: AutoMotoTestKit) -> None:
    repo = _create_repo(moto_testkit)
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


@use_moto_testkit(auto_start=True)
def test_delete_nonexistent_instance(moto_testkit: AutoMotoTestKit) -> None:
    repo = _create_repo(moto_testkit)
    with pytest.raises(ClientError):
        repo.delete_instance(db_instance_identifier="no-such-db")


@use_moto_testkit(auto_start=True)
def test_create_instance_with_tags(moto_testkit: AutoMotoTestKit) -> None:
    repo = _create_repo(moto_testkit)
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


@use_moto_testkit(auto_start=True)
def test_sqlite_create_insert_fetch(moto_testkit: AutoMotoTestKit) -> None:
    repo = _create_repo(moto_testkit)
    repo.create_table_sql("users", "id INTEGER PRIMARY KEY, name TEXT, email TEXT")
    repo.insert_record("users", ["name", "email"], ("Alice", "alice@example.com"))
    repo.insert_record("users", ["name", "email"], ("Bob", "bob@example.com"))
    rows = repo.fetch_all("users")
    assert len(rows) == 2
    assert rows[0]["name"] == "Alice"
    assert rows[1]["name"] == "Bob"
