from functools import cached_property
from typing import Any

from recurvedata.connectors._register import register_connector_class
from recurvedata.connectors.connectors.mysql import MysqlConnector
from recurvedata.connectors.const import ENV_VAR_DBT_PASSWORD, ENV_VAR_DBT_USER, SSH_TUNNEL_CONFIG_SCHEMA
from recurvedata.connectors.datasource import DataSourceWrapper
from recurvedata.connectors.dbapi import DBAPIBase, with_ssh_tunnel
from recurvedata.consts import ConnectorGroup
from recurvedata.core.translation import _l

CONNECTION_TYPE = "starrocks"
UI_CONNECTION_TYPE = "StarRocks"


@register_connector_class([CONNECTION_TYPE, UI_CONNECTION_TYPE])
class StarRocksConnector(MysqlConnector):
    SYSTEM_DATABASES = [
        "information_schema",
    ]
    connection_type = CONNECTION_TYPE
    ui_connection_type = UI_CONNECTION_TYPE
    group = [ConnectorGroup.DESTINATION]

    config_schema = {
        "type": "object",
        "properties": {
            "host": {
                "type": "string",
                "title": _l("Host Address"),
                "default": "127.0.0.1",
            },
            "user": {"type": "string", "title": _l("Username")},
            "password": {"type": "string", "title": _l("Password")},
            "database": {
                "type": "string",
                "title": _l("Database Name"),
                "description": _l("The name of the database to connect to"),
            },
            "port": {
                "type": "number",
                "title": _l("MySQL Port Number"),
                "description": _l("The port number for connecting to MySQL server on FE"),
                "default": 9030,
            },
            "http_port": {
                "type": "number",
                "title": _l("FE HTTP Port"),
                "description": _l("The HTTP port number for the Doris Frontend (FE) service"),
                "default": 8030,
            },
            "ssh_tunnel": SSH_TUNNEL_CONFIG_SCHEMA,
        },
        "order": ["host", "port", "http_port", "user", "password", "database", "ssh_tunnel"],
        "required": ["host", "http_port"],
        "secret": ["password"],
    }

    available_column_types = DBAPIBase.available_column_types + [
        # Numeric types
        "tinyint",
        "integer",  # alias for int
        "largeint",  # 128-bit signed integer
        "numeric",  # alias for decimal
        "real",  # alias for float
        "double precision",  # alias for double
        # String types
        "text",  # alias for string
        "string",  # alias for varchar
        "binary",
        "varbinary",
        # Date and Time types
        "datetime",  # alias for timestamp
        "time",
        # Complex types
        "array",
        "map",
        "struct",
        "json",
        # Special types
        "bitmap",
        "hll",
        # Boolean type
        "boolean",
        "bool",  # alias for boolean
    ]

    column_type_mapping = {
        "integer": ["tinyint", "largeint"],
        "string": ["text", "string"],
    }

    def convert_config_to_dbt_profile(self, database: str, schema: str = None) -> dict:
        return {
            "host": self.host,
            "port": self.port,
            "username": ENV_VAR_DBT_USER,
            "password": ENV_VAR_DBT_PASSWORD,
            "schema": database or self.database,
            "type": "starrocks",  # dbt-starrocks only support python<=3.10
        }

    def convert_config_to_cube_config(
        self, database: str, schema: str = None, datasource: DataSourceWrapper = None
    ) -> dict:
        return {
            "type": "mysql",
            "host": self.host,
            "port": self.port,
            "user": datasource.user,
            "password": datasource.password,
            "database": database or self.database,
        }

    @with_ssh_tunnel
    def get_columns(self, table, database=None):
        """
        Override get_columns method to properly handle StarRocks-specific data types
        """
        database = database or self.database
        # Use raw SQL query to get column information instead of relying on SQLAlchemy inspector
        query = f"""
        SELECT
            column_name,
            data_type,
            column_default,
            is_nullable,
            column_comment
        FROM information_schema.columns
        WHERE table_schema = '{database}'
        AND table_name = '{table}'
        """
        column_metas = []
        results = self.fetchall(query)
        for row in results:
            column_metas.append(
                {
                    "name": row[0],
                    "type": row[1].lower() if row[1] else "",
                    "default": row[2],
                    "nullable": row[3] == "YES",
                    "comment": row[4],
                }
            )

        return column_metas

    @cached_property
    @with_ssh_tunnel
    def type_code_mapping(self) -> dict:
        pass

    def sqlalchemy_column_type_code_to_name(self, type_code: Any, size: int | None = None) -> str:
        # values refer to https://docs.starrocks.io/docs/sql-reference/data-types/
        # values of this mapping must be in available_column_types, or just default as string
        from pymysql.constants import FIELD_TYPE

        type_code_mapping = {
            FIELD_TYPE.TINY: "tinyint",
            FIELD_TYPE.SHORT: "smallint",
            FIELD_TYPE.LONG: "int",
            FIELD_TYPE.FLOAT: "float",
            FIELD_TYPE.DOUBLE: "double",
            FIELD_TYPE.DECIMAL: "decimal",
            FIELD_TYPE.NEWDECIMAL: "decimal",
            FIELD_TYPE.LONGLONG: "bigint",
            FIELD_TYPE.INT24: "int",
            FIELD_TYPE.DATE: "date",
            FIELD_TYPE.NEWDATE: "date",
            FIELD_TYPE.DATETIME: "datetime",
            FIELD_TYPE.STRING: "varchar",
            FIELD_TYPE.VARCHAR: "varchar",
            FIELD_TYPE.JSON: "json",
        }
        return type_code_mapping.get(type_code, "string")
