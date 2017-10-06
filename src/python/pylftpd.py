# Copyright 2017, Inderpreet Singh, All rights reserved.

import signal
import sys
import time
import argparse

# my libs
from common import ServiceExit, PylftpContext, Constants, PylftpConfig, Patterns
from controller import Controller, ControllerJob, AutoQueue
from web import WebAppJob


class Pylftpd:
    """
    Implements the service for pylftp
    It is run in the main thread (no daemonization)
    """
    def __init__(self):
        # Parse the args
        args = self._parse_args()

        # Create context
        config = PylftpConfig.from_file(args.config)
        patterns = Patterns.from_file(args.patterns)
        self.context = PylftpContext(debug=args.debug,
                                     logdir=args.logdir,
                                     config=config,
                                     patterns=patterns)

        # Register the signal handlers
        signal.signal(signal.SIGTERM, self.signal)
        signal.signal(signal.SIGINT, self.signal)

        # Print context to log
        self.context.print_to_log()

    def run(self):
        self.context.logger.info("Starting pylftpd")

        # Create controller
        controller = Controller(self.context)

        # Create auto queue
        auto_queue = AutoQueue(self.context, controller)

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
            while True:
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

        self.context.logger.info("Finished pylftpd")

    def signal(self, signum: int, _):
        # noinspection PyUnresolvedReferences
        # Signals is a generated enum
        self.context.logger.info("Caught signal {}".format(signal.Signals(signum).name))
        raise ServiceExit()

    @staticmethod
    def _parse_args():
        parser = argparse.ArgumentParser(description="PyLFTP daemon")
        parser.add_argument("-c", "--config", required=True, help="Path to config file")
        parser.add_argument("-p", "--patterns", required=True, help="Path to patterns file")
        parser.add_argument("--logdir", help="Directory for log files")
        parser.add_argument("-d", "--debug", action="store_true", help="Enable debug logs")
        return parser.parse_args()


if __name__ == "__main__":
    if sys.hexversion < 0x03050000:
        sys.exit("Python 3.5 or newer is required to run this program.")

    pylftpd = Pylftpd()
    pylftpd.run()
