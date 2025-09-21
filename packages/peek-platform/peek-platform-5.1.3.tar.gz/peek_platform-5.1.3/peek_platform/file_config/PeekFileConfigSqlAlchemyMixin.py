import logging
import os

from jsoncfg.value_mappers import require_dict
from jsoncfg.value_mappers import require_integer
from jsoncfg.value_mappers import require_string
from setproctitle import getproctitle

logger = logging.getLogger(__name__)


class PeekFileConfigSqlAlchemyMixin:
    @property
    def dbConnectString(self):

        with self._cfg as c:
            if "PGHOST" in os.environ:
                eePgSocket = f"{os.environ['PGHOST']}"
                default = f"postgresql+psycopg://peek@/peek?host={eePgSocket}"
            else:
                default = "postgresql+psycopg://peek:PASSWORD@127.0.0.1/peek"

            return c.sqlalchemy.connectUrl(default, require_string)

    @property
    def dbEngineArgs(self):
        default = {
            "echo": False,  # Print every SQL statement executed
            "pool_size": 20,  # Number of connections to keep open
            "max_overflow": 50,
            # Number that the pool size can exceed when required
            "pool_timeout": 60,  # Timeout for getting conn from pool
            "pool_recycle": 600,  # Reconnect?? after 10 minutes
            # This supersedes 'use_batch_mode': True,
        }
        with self._cfg as c:
            val = c.sqlalchemy.engineArgs(default, require_dict)
            # Upgrade depreciated psycopg setting.
            if val.get("use_batch_mode") == True:
                del val["use_batch_mode"]
                c.sqlalchemy.engineArgs = val

            if "client_encoding" not in val:
                val["client_encoding"] = "utf8"
                c.sqlalchemy.engineArgs = val

            if "executemany_mode" in val:
                del val["executemany_mode"]

        statementTimeoutMs = self.dbSessionStatementSecondsTimeout * 1000
        idleTimeoutMs = self.dbSessionIdleSecondsTimeout * 1000

        dbEngineArgs = {
            "connect_args": {
                "application_name": f"{getproctitle()}_{os.getpid()}",
                "connect_timeout": 10,
                "options": (
                    f" -c statement_timeout={statementTimeoutMs}ms "
                    f" -c idle_in_transaction_session_timeout={idleTimeoutMs}ms"
                ),
            }
        }

        dbEngineArgs.update(val)

        return dbEngineArgs

    @property
    def dbSessionStatementSecondsTimeout(self):
        with self._cfg as c:
            default = 120
            return c.sqlalchemy.sessionStatementSecondsTimeout(
                default, require_integer
            )

    @property
    def dbSessionIdleSecondsTimeout(self):
        with self._cfg as c:
            default = 120
            return c.sqlalchemy.sessionIdleSecondsTimeout(
                default, require_integer
            )
