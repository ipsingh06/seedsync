# Copyright 2017, Inderpreet Singh, All rights reserved.

import signal
import time
import logging
import sys
import argparse
import os
from logging.handlers import RotatingFileHandler
from configparser import ConfigParser

# my libs
from common import Config, Patterns
from common import PylftpError, PylftpContext
from pylftpmainjob import PylftpMainJob
from web_app import WebAppJob


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
    _WEB_ACCESS_LOG_NAME = 'web_access'

    def __init__(self):
        # Parse arguments
        parser = argparse.ArgumentParser(description="PyLFTP daemon")
        parser.add_argument("-c", "--config", required=True, help="Path to config file")
        parser.add_argument("-p", "--patterns", required=True, help="Path to patterns file")
        parser.add_argument("--logdir", help="Directory for log files")
        parser.add_argument("-d", "--debug", action="store_true", help="Enable debug logs")
        args = parser.parse_args()

        # Logger setup
        # We separate the main log from the web-access log
        logger = self.create_logger(name=Pylftpd._SERVICE_NAME,
                                    debug=args.debug,
                                    logdir=args.logdir)
        web_access_logger = self.create_logger(name=Pylftpd._WEB_ACCESS_LOG_NAME,
                                               debug=args.debug,
                                               logdir=args.logdir)

        # Load config
        config = self.load_config(args.config)
        # Load patterns
        patterns = self.load_patterns(args.patterns)

        # Create context
        self.context = PylftpContext(
            args=args,
            logger=logger,
            web_access_logger=web_access_logger,
            config=config,
            patterns=patterns
        )

        # Register the signal handlers
        signal.signal(signal.SIGTERM, self.signal)
        signal.signal(signal.SIGINT, self.signal)

        # Print context to log
        self.context.print_to_log()

    @staticmethod
    def create_logger(name: str, debug: bool, logdir: str) -> logging.Logger:
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG if debug else logging.INFO)
        if logdir is not None:
            # Output logs to a file in the given directory
            handler = RotatingFileHandler(
                        "{}/{}.log".format(logdir, name),
                        maxBytes=Pylftpd._MAX_LOG_SIZE_IN_BYTES,
                        backupCount=Pylftpd._LOG_BACKUP_COUNT
                      )
        else:
            handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    @staticmethod
    def load_config(config_file_path: str) -> Config:
        if not os.path.isfile(config_file_path):
            raise PylftpError("Config file not found: {}".format(config_file_path))
        config_parser = ConfigParser()
        config_parser.read(config_file_path)
        config = {}
        for section in config_parser.sections():
            config[section] = {}
            for option in config_parser.options(section):
                config[section][option] = config_parser.get(section, option)
        return config

    @staticmethod
    def load_patterns(patterns_file_path: str) -> Patterns:
        if not os.path.isfile(patterns_file_path):
            raise PylftpError("Patterns file not found: {}".format(patterns_file_path))
        with open(patterns_file_path) as f:
            patterns = [x.strip() for x in f.readlines()]
        return patterns

    def run(self):
        self.context.logger.info("Starting pylftpd")

        # Define child threads
        pylftp_job = PylftpMainJob(
            context=self.context.create_child_context(PylftpMainJob.__name__)
        )
        webapp_job = WebAppJob(
            context=self.context.create_child_context(WebAppJob.__name__)
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
