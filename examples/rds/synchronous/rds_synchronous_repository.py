import sqlite3
import time
from typing import Any, Union

import boto3


class RDSRepository:
    def __init__(self, endpoint_url: str, region_name: str = "eu-central-1"):
        self.endpoint_url = endpoint_url
        self.region_name = region_name
        self._client = boto3.client(
            "rds", region_name=self.region_name, endpoint_url=self.endpoint_url
        )

    def create_instance(
        self,
        *,
        db_instance_identifier: str,
        engine: str,
        db_instance_class: str,
        master_username: Union[str, None] = None,
        master_user_password: Union[str, None] = None,
        allocated_storage: Union[int, None] = None,
        publicly_accessible: bool = False,
        tags: Union[dict[str, str] , None] = None,
        wait: bool = True,
        wait_timeout_seconds: float = 60.0,
    ) -> dict:
        params: dict[str, Any] = {
            "DBInstanceIdentifier": db_instance_identifier,
            "Engine": engine,
            "DBInstanceClass": db_instance_class,
            "PubliclyAccessible": publicly_accessible,
        }
        if master_username:
            params["MasterUsername"] = master_username
        if master_user_password:
            params["MasterUserPassword"] = master_user_password
        if allocated_storage is not None:
            params["AllocatedStorage"] = allocated_storage
        if tags:
            params["Tags"] = [{"Key": k, "Value": v} for k, v in tags.items()]

        resp = self._client.create_db_instance(**params)
        instance = resp.get("DBInstance", {})

        if wait:
            start = time.time()
            while time.time() - start < wait_timeout_seconds:
                inst = self.describe_instance(db_instance_identifier)
                if inst and inst.get("DBInstanceStatus") == "available":
                    return inst
                time.sleep(2)
        return instance

    def describe_instance(self, db_instance_identifier: str) -> Union[dict, None]:
        resp = self._client.describe_db_instances(
            DBInstanceIdentifier=db_instance_identifier
        )
        items = resp.get("DBInstances", [])
        return items[0] if items else None

    def list_instances(self) -> list[dict]:
        paginator = self._client.get_paginator("describe_db_instances")
        out: list[dict] = []
        for page in paginator.paginate():
            out.extend(page.get("DBInstances", []))
        return out

    def delete_instance(
        self, *, db_instance_identifier: str, skip_final_snapshot: bool = True
    ) -> dict:
        params = {
            "DBInstanceIdentifier": db_instance_identifier,
            "SkipFinalSnapshot": skip_final_snapshot,
        }
        resp = self._client.delete_db_instance(**params)
        return resp.get("DBInstance", {})

    def connect_db_sqlite(self):
        """Conecta a um banco SQLite em memória (para testes)."""
        self._db_conn = sqlite3.connect(":memory:")
        self._db_conn.row_factory = sqlite3.Row
        return self._db_conn

    def create_table_sql(self, table_name: str, columns_sql: str):
        with self._db_conn:
            self._db_conn.execute(
                f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_sql});"
            )

    def insert_record(self, table_name: str, columns: list[str], values: tuple):
        cols = ", ".join(columns)
        placeholders = ", ".join(["?"] * len(values))
        with self._db_conn:
            self._db_conn.execute(
                f"INSERT INTO {table_name} ({cols}) VALUES ({placeholders});", values
            )

    def fetch_all(self, table_name: str):
        cur = self._db_conn.execute(f"SELECT * FROM {table_name};")
        return [dict(row) for row in cur.fetchall()]
