import abc
from typing import Optional

import pandas as pd

from pyrasgo.api.session import Session
from pyrasgo.storage.dataframe import utils as dfutils


class DataWarehouse(metaclass=abc.ABCMeta):
    @property
    @abc.abstractmethod
    def user_connection(self):
        pass

    @property
    @abc.abstractmethod
    def user_credentials(self):
        pass

    @abc.abstractmethod
    def get_source_table(self, table_name: str, database: Optional[str] = None, schema: Optional[str] = None,
                         record_limit: Optional[int] = None) -> pd.DataFrame:
        # TODO: This likely should not be "table" for s3 storage
        pass

    @abc.abstractmethod
    def get_source_tables(self, database: Optional[str] = None, schema: Optional[str] = None) -> pd.DataFrame:
        # TODO: This likely should not be "tables" for s3 storage
        pass

    @abc.abstractmethod
    def get_source_columns(self, table: Optional[str] = None, database: Optional[str] = None, schema: Optional[str] = None, data_type: Optional[str] = None) -> pd.DataFrame:
        pass

    @abc.abstractmethod
    def _write_dataframe_to_table(self, df: pd.DataFrame, *,
                                  table_name: str,
                                  append: Optional[bool] = False):
        pass

    @staticmethod
    def _make_select_statement(table_metadata: dict, filters: dict, limit: Optional[int] = None, columns: str = '*') -> tuple:
        """
        Constructs select * query for table
        """
        query = f"SELECT {columns} FROM "
        query = query + "{database}.{schema}.{table}".format(**table_metadata)
        values = []
        if filters:
            comparisons = []
            for k, v in filters.items():
                if isinstance(v, list):
                    comparisons.append(f"{k} IN ({', '.join(['%s'] * len(v))})")
                    values += v
                elif v[:1] in ['>', '<', '='] \
                        or v[:2] in ['>=', '<=', '<>', '!='] \
                        or v[:4] == 'IN (' \
                        or v[:8] == 'BETWEEN ':
                    comparisons.append(f'{k} {v}')
                else:
                    comparisons.append(f"{k}=%s")
                    values.append(v)
            query += " WHERE " + " and ".join(comparisons)
        if limit:
            query += " LIMIT {}".format(limit)
        return query, values

    @classmethod
    def connect(cls):
        """
        Returns an instance of the account's Data Warehouse connection
        :param session: Session object describing the current user's session
        :return:
        """
        # TODO: Provide the setup for other warehouses here:
        from pyrasgo.storage import SnowflakeDataWarehouse

        return SnowflakeDataWarehouse()

    def write_dataframe_to_table(self, df: pd.DataFrame, *,
                                 table_name: str,
                                 append: Optional[bool] = False):
        with self.user_connection.cursor() as cursor:
            cursor.execute(dfutils.generate_ddl(df=df, table_name=table_name, append=append))
        self._write_dataframe_to_table(df=df, table_name=table_name, append=append)


class DataWarehouseSession(type(DataWarehouse), type(Session)):
    pass
