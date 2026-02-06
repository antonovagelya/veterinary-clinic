import psycopg2
from psycopg2.extensions import connection
from typing import Optional


class Database:
    """Класс для подключения к PostgreSQL"""

    def __init__(
        self,
        host: str,
        port: int,
        database: str,
        user: str,
        password: str
    ):
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self._connection: Optional[connection] = None

    def connect(self) -> None:
        """Устанавливает соединение с БД"""
        if self._connection is None:
            self._connection = psycopg2.connect(
                host=self.host,
                port=self.port,
                dbname=self.database,
                user=self.user,
                password=self.password
            )

    def get_connection(self) -> connection:
        """Возвращает активное соединение с БД"""
        if self._connection is None:
            raise RuntimeError("Не удалось установить соединение с базой данных")
        return self._connection

    def close(self) -> None:
        """Закрывает соединение с БД"""
        if self._connection is not None:
            self._connection.close()
            self._connection = None
