# Copyright 2017, Inderpreet Singh, All rights reserved.

import signal
import sys
import time
import argparse
import os
import logging
from datetime import datetime
from logging.handlers import RotatingFileHandler
from typing import Optional

# my libs
from common import ServiceExit, PylftpContext, Constants, PylftpConfig, PylftpArgs
from controller import Controller, ControllerJob, ControllerPersist, AutoQueue, AutoQueuePersist
from web import WebAppJob


class Pylftpd:
    """
    Implements the service for pylftp
    It is run in the main thread (no daemonization)
    """
    __FILE_CONFIG = "settings.cfg"
    __FILE_AUTO_QUEUE_PERSIST = "autoqueue.persist"
    __FILE_CONTROLLER_PERSIST = "controller.persist"

    # This logger is used to print any exceptions caught at top module
    logger = None

    def __init__(self):
        # Parse the args
        args = self._parse_args()

        # Path to html resources
        self.html_path = args.html

        # Logger setup
        # We separate the main log from the web-access log
        logger = self._create_logger(name=Constants.SERVICE_NAME,
                                     debug=args.debug,
                                     logdir=args.logdir)
        Pylftpd.logger = logger
        web_access_logger = self._create_logger(name=Constants.WEB_ACCESS_LOG_NAME,
                                                debug=args.debug,
                                                logdir=args.logdir)

        # Create context args
        ctx_args = PylftpArgs()
        ctx_args.local_path_to_scanfs = args.scanfs

        # Create context
        config = PylftpConfig.from_file(os.path.join(args.config_dir, Pylftpd.__FILE_CONFIG))
        self.context = PylftpContext(logger=logger,
                                     web_access_logger=web_access_logger,
                                     config=config,
                                     args=ctx_args)

        # Register the signal handlers
        signal.signal(signal.SIGTERM, self.signal)
        signal.signal(signal.SIGINT, self.signal)

        # Print context to log
        self.context.print_to_log()

        # Load the persists
        self.controller_persist_path = os.path.join(args.config_dir, Pylftpd.__FILE_CONTROLLER_PERSIST)
        if os.path.isfile(self.controller_persist_path):
            self.controller_persist = ControllerPersist.from_file(self.controller_persist_path)
        else:
            self.controller_persist = ControllerPersist()
        self.auto_queue_persist_path = os.path.join(args.config_dir, Pylftpd.__FILE_AUTO_QUEUE_PERSIST)
        if os.path.isfile(self.auto_queue_persist_path):
            self.auto_queue_persist = AutoQueuePersist.from_file(self.auto_queue_persist_path)
        else:
            self.auto_queue_persist = AutoQueuePersist()

    def run(self):
        self.context.logger.info("Starting pylftpd")

        # Create controller
        controller = Controller(self.context, self.controller_persist)

        # Create auto queue
        auto_queue = AutoQueue(self.context, self.auto_queue_persist, controller)

        # Define child threads
        controller_job = ControllerJob(
            context=self.context.create_child_context(ControllerJob.__name__),
            controller=controller,
            auto_queue=auto_queue
        )
        webapp_job = WebAppJob(
            context=self.context.create_child_context(WebAppJob.__name__),
            controller=controller,
            html_path=self.html_path
        )

        try:
            # Start child threads here
            controller_job.start()
            webapp_job.start()

            prev_persist_timestamp = datetime.now()

            # Thread loop
            while True:
                # Persist to file occasionally
                now = datetime.now()
                if (now - prev_persist_timestamp).total_seconds() > Constants.MIN_PERSIST_TO_FILE_INTERVAL_IN_SECS:
                    prev_persist_timestamp = now
                    self.persist()

                # Propagate exceptions
                controller_job.propagate_exception()
                webapp_job.propagate_exception()

                # Nothing else to do
                time.sleep(Constants.MAIN_THREAD_SLEEP_INTERVAL_IN_SECS)

        except Exception as exc:
            self.context.logger.info("Exiting pylftp")

            # This sleep is important to allow the jobs to finish setup before we terminate them
            # If we kill too early, the jobs may leave lingering threads around
            # Note: There might be a better way to ensure that job setup has completed, but this
            #       will do for now
            time.sleep(Constants.MAIN_THREAD_SLEEP_INTERVAL_IN_SECS)

            # Join all the threads here
            controller_job.terminate()
            webapp_job.terminate()

            # Wait for the threads to close
            controller_job.join()
            webapp_job.join()

            # Stop any threads/process in controller
            controller.exit()

            # Raise any exceptions so they can be logged properly
            if not isinstance(exc, ServiceExit):
                raise

        self.persist()
        self.context.logger.info("Finished pylftpd")

    def persist(self):
        # Save the persists
        self.context.logger.debug("Persisting states to file")
        self.controller_persist.to_file(self.controller_persist_path)
        self.auto_queue_persist.to_file(self.auto_queue_persist_path)

    def signal(self, signum: int, _):
        # noinspection PyUnresolvedReferences
        # Signals is a generated enum
        self.context.logger.info("Caught signal {}".format(signal.Signals(signum).name))
        raise ServiceExit()

    @staticmethod
    def _parse_args():
        parser = argparse.ArgumentParser(description="PyLFTP daemon")
        parser.add_argument("-c", "--config_dir", required=True, help="Path to config directory")
        parser.add_argument("--logdir", help="Directory for log files")
        parser.add_argument("-d", "--debug", action="store_true", help="Enable debug logs")

        # Whether package is frozen
        is_frozen = getattr(sys, 'frozen', False)

        # Html path is only required if not running a frozen package
        # For a frozen package, set default to root/html
        # noinspection PyUnresolvedReferences
        # noinspection PyProtectedMember
        default_html_path = os.path.join(sys._MEIPASS, "html") if is_frozen else None
        parser.add_argument("--html",
                            required=not is_frozen,
                            default=default_html_path,
                            help="Path to directory containing html resources")

        # Scanfs path is only required if not running a frozen package
        # For a frozen package, set default to root/scanfs
        # noinspection PyUnresolvedReferences
        # noinspection PyProtectedMember
        default_scanfs_path = os.path.join(sys._MEIPASS, "scanfs") if is_frozen else None
        parser.add_argument("--scanfs",
                            required=not is_frozen,
                            default=default_scanfs_path,
                            help="Path to scanfs executable")

        return parser.parse_args()

    @staticmethod
    def _create_logger(name: str, debug: bool, logdir: Optional[str]) -> logging.Logger:
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG if debug else logging.INFO)
        if logdir is not None:
            # Output logs to a file in the given directory
            handler = RotatingFileHandler(
                        "{}/{}.log".format(logdir, name),
                        maxBytes=Constants.MAX_LOG_SIZE_IN_BYTES,
                        backupCount=Constants.LOG_BACKUP_COUNT
                      )
        else:
            handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger


if __name__ == "__main__":
    if sys.hexversion < 0x03050000:
        sys.exit("Python 3.5 or newer is required to run this program.")

    try:
        pylftpd = Pylftpd()
        pylftpd.run()
    except Exception as e:
        if Pylftpd.logger is not None:
            Pylftpd.logger.exception("Caught exception")
        raise
