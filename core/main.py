import setup_path
import asyncio as aio
import getopt
import os
import sys
from typing import List

import daemon
from daemon import pidfile

import global_event_loop as gloop
import config as cfg
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

    def initialize(self) -> bool:
        try:
            self.init_argv_params()
            self.init_config()
        except Exception as ex:
            LOG.error(ex.args[-1])
            return False
        return True

    def is_daemon(self):
        return self.is_run_background

    def release(self) -> bool:
        try:
            if self.loop and self.loop.is_running():
                self.loop.stop()
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
        LOG.info("After init argv param. Config filename: {}, run in background: {}"
                 .format(self.config_filename, self.is_run_background))

    def init_config(self):
        LOG.info("Config file:{}".format(self.config_filename))
        cfg.init_global_config(self.config_filename)

    def run(self) -> bool:
        self._async_start()
        return True

    def _async_start(self):
        timer = async_timer.Timer(self.awake, timeout_sec=0)
        if not timer.start():
            LOG.error("{} - unknown error".format(LOG.func_name()))
            sys.exit(2)
        self.loop.run_forever()

    def start(self):
        host = cfg.global_core_conf.get("Exchange", "host", fallback="https://api.binance.com")
        LOG.debug("Starting tasks for application for host:{}".format(host))
        if "binance" in host:
            worker = exchange_factory.ExchangeFactory.create_exchange(
                exchange_factory.Exchanges.BINANCE,
                config=cfg.global_core_conf
            )
            if worker:
                LOG.info("Starting worker...")
                try:
                    worker.run_worker()
                except Exception as ex:
                    LOG.error("Unknown error has occured in worker:{}".format(ex.args[-1]))
            else:
                LOG.error("Invalid worker object!")
        else:
            LOG.error("Did't set a name of working exchange! Abort")
            sys.exit(1)
        timer = async_timer.Timer(self.awake, cfg.global_core_conf.getint("Exchange", "awake_timeout_sec", fallback=300))
        if not timer.start():
            sys.exit(2)

    def awake(self, future: aio.Future):
        if future:
            self.start()
        else:
            LOG.error("{} - Invalid future. Aborting...".format(LOG.func_name()))
            sys.exit(4)


def main(argv):
    app = Application(argv, loop=gloop.global_ev_loop)
    try:
        app.initialize()
        if app.is_daemon():
            file_pid_lock = __file__ + ".lock"
            LOG.info("Daemonize this application. File lock:{}".format(file_pid_lock))
            with daemon.DaemonContext(
                working_directory=os.getcwd(),  # Get working dir
                umask=0o002,
                pidfile=pidfile.PIDLockFile(file_pid_lock),  # Create a pid file
                files_preserve=[LOG.log_file_handler.stream, ],  # Keep the logger file after fork
            ):
                app.run()
        else:
            app.run()

    finally:
        app.release()


if __name__ == "__main__":
    main(sys.argv[1:])
