import pytest
from botocore.exceptions import ClientError

from examples.rds.synchronous.rds_synchronous_repository import \
    RDSRepository
from src import MotoTestKit


@pytest.fixture
def moto_testkit_fixture() -> RDSRepository:
    """Inicializa MotoTestKit e repositório RDS para testes."""
    moto_testkit = MotoTestKit(auto_start=True)
    repository = RDSRepository(
        endpoint_url=moto_testkit.get_client("rds").meta.endpoint_url
    )
    repository.connect_db_sqlite()
    yield repository
    moto_testkit.stop()


def test_create_and_list_rds(moto_testkit_fixture: RDSRepository) -> None:
    created = moto_testkit_fixture.create_instance(
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
    listed = moto_testkit_fixture.list_instances()
    assert any(i["DBInstanceIdentifier"] == "testdb" for i in listed)


def test_delete_rds_instance(moto_testkit_fixture: RDSRepository) -> None:
    moto_testkit_fixture.create_instance(
        db_instance_identifier="testdb",
        engine="postgres",
        db_instance_class="db.t3.micro",
        master_username="postgres",
        master_user_password="secret123!",
        allocated_storage=20,
        publicly_accessible=False,
        wait=False,
    )
    deleted = moto_testkit_fixture.delete_instance(db_instance_identifier="testdb")
    assert deleted["DBInstanceIdentifier"] == "testdb"


def test_describe_instance(moto_testkit_fixture: RDSRepository) -> None:
    moto_testkit_fixture.create_instance(
        db_instance_identifier="descdb",
        engine="postgres",
        db_instance_class="db.t3.micro",
        master_username="postgres",
        master_user_password="secret123!",
        allocated_storage=20,
        wait=False,
    )
    desc = moto_testkit_fixture.describe_instance("descdb")
    assert desc is not None
    assert desc["DBInstanceIdentifier"] == "descdb"


def test_list_instances_empty(moto_testkit_fixture: RDSRepository) -> None:
    assert moto_testkit_fixture.list_instances() == []


def test_create_multiple_instances(moto_testkit_fixture: RDSRepository) -> None:
    ids = ["db1", "db2", "db3"]
    for db_id in ids:
        moto_testkit_fixture.create_instance(
            db_instance_identifier=db_id,
            engine="postgres",
            db_instance_class="db.t3.micro",
            master_username="postgres",
            master_user_password="secret123!",
            allocated_storage=20,
            wait=False,
        )
    listed_ids = [
        i["DBInstanceIdentifier"] for i in moto_testkit_fixture.list_instances()
    ]
    for db_id in ids:
        assert db_id in listed_ids


def test_delete_nonexistent_instance(moto_testkit_fixture: RDSRepository) -> None:
    with pytest.raises(ClientError):
        moto_testkit_fixture.delete_instance(db_instance_identifier="no-such-db")


def test_create_instance_with_tags(moto_testkit_fixture: RDSRepository) -> None:
    tags = {"env": "dev", "owner": "qa-team"}
    created = moto_testkit_fixture.create_instance(
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


def test_sqlite_create_insert_fetch(moto_testkit_fixture: RDSRepository) -> None:
    moto_testkit_fixture.create_table_sql(
        "users", "id INTEGER PRIMARY KEY, name TEXT, email TEXT"
    )
    moto_testkit_fixture.insert_record(
        "users", ["name", "email"], ("Alice", "alice@example.com")
    )
    moto_testkit_fixture.insert_record(
        "users", ["name", "email"], ("Bob", "bob@example.com")
    )

    rows = moto_testkit_fixture.fetch_all("users")
    assert len(rows) == 2
    assert rows[0]["name"] == "Alice"
    assert rows[1]["name"] == "Bob"
