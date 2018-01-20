import asyncio as aio
import getopt
import os
import sys
from typing import List

import daemon
from daemon import pidfile

import async_db_adapter as db
import global_event_loop as gloop
from core import config as cfg
from logger import logger
from services import exchange_factory
from utils import async_timer

LOG = logger.LOG


class Application(object):
    def __init__(self, argv: List[str], loop=gloop.global_ev_loop):
        self.argv = argv
        self.loop = loop
        self.config_filename = None
        self.is_run_background = None
        self.daemon_context = None
        self.pg_connection = None

    def initialize(self) -> bool:
        try:
            self.init_argv_params()
            self.init_config()
            self.init_daemon_context()
            #self.init_bd_connection()
        except Exception as ex:
            LOG.error(ex.args[-1])
            return False
        return True

    def release(self) -> bool:
        try:
            if self.loop and self.loop.is_running():
                self.loop.stop()
            if self.daemon_context:
                self.daemon_context.close()
            if self.pg_connection:
                self.pg_connection.close()
        except Exception as ex:
            LOG.error(ex.args[-1])
            return False
        return True

    def init_argv_params(self):
        optlist, args = getopt.getopt(self.argv, "hbc:", ["config="])
        for opt, arg in optlist:  # Parsing command line options
            if opt == '-h':
                raise ValueError(__file__ + " -c <config_file>")
            elif opt in ("-c", "--config"):
                self.config_filename = arg
            elif opt in ("-b", "--background"):
                self.is_run_background = True
            else:
                raise ValueError(__file__ + " -c <config_file>")

    def init_config(self):
        cfg.init_global_config(self.config_filename)

    def init_daemon_context(self):
        if self.is_run_background:
            file_pid_lock = __file__ + ".lock"
            LOG.info('Daemonize this application')
            self.daemon_context = daemon.DaemonContext(
                working_directory=os.getcwd(),  # Get working dir
                umask=0o002,
                pidfile=pidfile.PIDLockFile(file_pid_lock),  # Create a pid file
                files_preserve=[LOG.log_file_handler.stream, ],  # Keep the logger file after fork
            )

    def init_bd_connection(self):
        gloop.push_async_task(callback_func=self.on_db_connection_done, run_func=db.async_create_pg_conn)
        self.loop.run_forever()

    def on_db_connection_done(self, future: aio.Future):
        if not future.result():
            LOG.error("Error with opening DB. Terminate application")
            sys.exit(1)
        LOG.debug("init_bd_coonection: {}".format(future.result()))
        self.pg_connection = future.result()
        self.start()

    def run(self) -> bool:
        if not self.initialize():
            sys.exit(1)
        self.start()
        return True

    def start(self):
        LOG.debug("Starting tasks for application")
        host = cfg.global_core_conf.get("Exchange", "host", fallback="https://api.binance.com")
        if "binance" in host:
            worker = exchange_factory.ExchangeFactory.create_exchange(
                exchange_factory.Exchanges.BINANCE,
                config=cfg.global_core_conf
            )
            if worker:
                worker.run_worker()
            else:
                LOG.error("Invalid worker object!")
        else:
            LOG.error("Did't set a name of working exchange! Abort")
            sys.exit(1)
        timer = async_timer.Timer(self.awake, cfg.global_core_conf.get("Exchange", "awake_timeout_sec", fallback=300))
        timer.start()
        self.loop.run_forever()


    def awake(self, future: aio.Future):
        self.start()


def main(argv):
    app = Application(argv, loop=gloop.global_ev_loop)
    try:
        app.run()
    finally:
        app.release()


if __name__ == "__main__":
    main(sys.argv[1:])
