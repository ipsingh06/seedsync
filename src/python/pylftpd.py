# Copyright 2017, Inderpreet Singh, All rights reserved.

import signal
import sys
import time
import argparse
import os
from datetime import datetime

# my libs
from common import ServiceExit, PylftpContext, Constants, PylftpConfig
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

    def __init__(self):
        # Parse the args
        args = self._parse_args()

        # Create context
        config = PylftpConfig.from_file(os.path.join(args.config_dir, Pylftpd.__FILE_CONFIG))
        self.context = PylftpContext(debug=args.debug,
                                     logdir=args.logdir,
                                     config=config)

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
            controller=controller
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

                # Nothing else to do
                time.sleep(Constants.MAIN_THREAD_SLEEP_INTERVAL_IN_SECS)

        except ServiceExit:
            # Join all the threads here
            controller_job.terminate()
            webapp_job.terminate()

            # Wait for the threads to close
            controller_job.join()
            webapp_job.join()

            # Stop any threads/process in controller
            controller.exit()

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
        return parser.parse_args()


if __name__ == "__main__":
    if sys.hexversion < 0x03050000:
        sys.exit("Python 3.5 or newer is required to run this program.")

    pylftpd = Pylftpd()
    pylftpd.run()
