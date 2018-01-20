import aiopg
from core import config as gconf
from core import global_event_loop as gloop
from logger import logger
import datetime

LOG = logger.LOG
debug = False
dsn = 'dbname={} user={} password={} host={}'.format(
    gconf.global_core_conf.get("Postgres", "database", fallback="mycapp"),
    gconf.global_core_conf.get("Postgres", "user", fallback="local_test"),
    gconf.global_core_conf.get("Postgres", "password", fallback="test"),
    gconf.global_core_conf.get("Postgres", "host", fallback="127.0.0.1")
)
pg_connection = None


def now():
    return datetime.datetime.now()


def close_pg_conn():
    if pg_connection and not pg_connection.closed():
        pg_connection.close()


async def async_create_pg_conn(timeout: int = 20):
    LOG.debug("Create new connection")
    global pg_connection
    if pg_connection and not pg_connection.closed():
        pg_connection.close()
    if not pg_connection:
        pg_connection = await aiopg.connect(dsn=dsn, timeout=timeout)
        LOG.debug("New connection has created: {}".format(str(pg_connection)))
    return pg_connection


async def async_execute(query: str, bind_params: tuple=None, timeout=20):
    if not pg_connection or pg_connection.closed():
        LOG.error("Pg connection isn't initialize. Unable to perform request!")
        raise RuntimeError("Pg connection isn't initialize. Unable to perform request!")
    async with pg_connection.cursor() as cursor:
        await cursor.execute(query, bind_params, timeout=timeout)
        ret = []
        if cursor.rowcount != -1:
            async for row in cursor:
                ret.append(row)
        if debug:
            print(ret)
        return ret


# Testing
if __name__ == '__main__':
    def callback(future):
        print(future.result())

    debug = True
    query1 = """INSERT INTO mycapp.test 
            (fscontext_id,  
            fiplatform_id,
            faanswer_time) 
            VALUES (%s, %s, %s); commit"""

    query2 = "SELECT * FROM mycapp.test"
    params = ("asdasd", 411165, now())
    params1 = ("sd", 65, now())
    gloop.global_ev_loop.run_until_complete(async_create_pg_conn())
    # gloop.global_ev_loop.run_until_complete(async_execute(query1, params))
    # gloop.global_ev_loop.run_until_complete(async_execute(query1, params))
