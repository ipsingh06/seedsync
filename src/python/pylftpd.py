# Copyright 2017, Inderpreet Singh, All rights reserved.

import signal
import time
import logging
from logging.handlers import RotatingFileHandler
import sys
import argparse

# my libs
from common import PylftpContext
from pylftp import Pylftp
from web_app import WebApp


class ServiceExit(Exception):
    """
    Custom exception which is used to trigger the clean exit
    of all running threads and the main program.
    """
    pass


class Pylftpd:
    """
    Implements the service for pylftp
    It is run in the main thread (no daemonization)
    """
    _SERVICE_NAME = 'pylftp'
    _MAIN_THREAD_SLEEP_INTERVAL_IN_SECS = 0.5
    _MAX_LOG_SIZE_IN_BYTES = 10*1024*1024  # 10 MB
    _LOG_BACKUP_COUNT = 10

    def __init__(self):
        # Parse arguments
        parser = argparse.ArgumentParser(description="PyLFTP daemon")
        parser.add_argument("--logdir", help="Directory for log files")
        parser.add_argument("--debug", action="store_true", help="Enable debug logs")
        args = parser.parse_args()

        # Logger setup
        logger = logging.getLogger(Pylftpd._SERVICE_NAME)
        if args.debug:
            logger.setLevel(logging.DEBUG)
        else:
            logger.setLevel(logging.INFO)
        if args.logdir:
            # Output logs to a file in the given directory
            handler = RotatingFileHandler(
                        "{}/{}.log".format(args.logdir, Pylftpd._SERVICE_NAME),
                        maxBytes=Pylftpd._MAX_LOG_SIZE_IN_BYTES,
                        backupCount=Pylftpd._LOG_BACKUP_COUNT
                      )
        else:
            handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        self.context = PylftpContext(
            args=args,
            logger=logger
        )

        # Register the signal handlers
        signal.signal(signal.SIGTERM, self.signal)
        signal.signal(signal.SIGINT, self.signal)

    def run(self):
        self.context.logger.info("Starting pylftpd")

        # Define child threads
        pylftp_job = Pylftp(
            context=self.context.create_child_context(Pylftp.__name__)
        )
        webapp_job = WebApp(
            context=self.context.create_child_context(WebApp.__name__)
        )

        try:
            # Start child threads here
            pylftp_job.start()
            webapp_job.start()
            while True:
                time.sleep(Pylftpd._MAIN_THREAD_SLEEP_INTERVAL_IN_SECS)
        except ServiceExit:
            # Join all the threads here
            pylftp_job.terminate()
            webapp_job.terminate()

            # Wait for the threads to close
            pylftp_job.join()
            webapp_job.join()

        self.context.logger.info("Finished pylftpd")

    def signal(self, signum: int, _):
        self.context.logger.info("Caught signal {}".format(signal.Signals(signum).name))
        raise ServiceExit()


if __name__ == "__main__":
    if sys.hexversion < 0x03050000:
        sys.exit("Python 3.5 or newer is required to run this program.")

    pylftpd = Pylftpd()
    pylftpd.run()
