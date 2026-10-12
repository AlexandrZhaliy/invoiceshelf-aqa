"""Read-only access to the application database, for tests that compare stored data with the API.

Plain SQL through the PyMySQL driver (an entire ORM would only add noise for a couple of SELECTs)
"""

import pymysql
from pymysql.cursors import DictCursor
from framework.config import settings


class Database:
    def __init__(self) -> None:
        self.connection = pymysql.connect(
            host=settings.db_host,
            port=settings.db_port,
            user=settings.db_user,
            password=settings.db_password,
            database=settings.db_name,
            cursorclass=DictCursor,
            autocommit=True,  # every query sees the latest committed data, no stale snapshot
        )

    def fetch_one(self, sql: str, params: tuple = ()) -> dict | None:
        with self.connection.cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.fetchone()

    def close(self) -> None:
        self.connection.close()