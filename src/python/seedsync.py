# Copyright 2017, Inderpreet Singh, All rights reserved.

import signal
import sys
import time
import argparse
import os
import logging
from datetime import datetime
from logging.handlers import RotatingFileHandler
from typing import Optional, Type, TypeVar
import shutil

# my libs
from common import ServiceExit, Context, Constants, Config, Args, AppError
from common import ServiceRestart
from common import Localization, Status, ConfigError, Persist, PersistError
from controller import Controller, ControllerJob, ControllerPersist, AutoQueue, AutoQueuePersist
from web import WebAppJob, WebAppBuilder


T_Persist = TypeVar('T_Persist', bound=Persist)


class Seedsync:
    """
    Implements the service for seedsync
    It is run in the main thread (no daemonization)
    """
    __FILE_CONFIG = "settings.cfg"
    __FILE_AUTO_QUEUE_PERSIST = "autoqueue.persist"
    __FILE_CONTROLLER_PERSIST = "controller.persist"
    __CONFIG_DUMMY_VALUE = "<replace me>"

    # This logger is used to print any exceptions caught at top module
    logger = None

    def __init__(self):
        # Parse the args
        args = self._parse_args()

        # Create/load config
        config = None
        self.config_path = os.path.join(args.config_dir, Seedsync.__FILE_CONFIG)
        create_default_config = False
        if os.path.isfile(self.config_path):
            try:
                config = Config.from_file(self.config_path)
            except (ConfigError, PersistError):
                Seedsync.__backup_file(self.config_path)
                # set config to default
                create_default_config = True
        else:
            create_default_config = True

        if create_default_config:
            # Create default config
            config = Seedsync._create_default_config()
            config.to_file(self.config_path)

        # Determine the true value of debug
        is_debug = args.debug or config.general.debug

        # Create context args
        ctx_args = Args()
        ctx_args.local_path_to_scanfs = args.scanfs
        ctx_args.html_path = args.html
        ctx_args.debug = is_debug

        # Logger setup
        # We separate the main log from the web-access log
        logger = self._create_logger(name=Constants.SERVICE_NAME,
                                     debug=is_debug,
                                     logdir=args.logdir)
        Seedsync.logger = logger
        web_access_logger = self._create_logger(name=Constants.WEB_ACCESS_LOG_NAME,
                                                debug=is_debug,
                                                logdir=args.logdir)
        logger.info("Debug mode is {}.".format("enabled" if is_debug else "disabled"))

        # Create status
        status = Status()

        # Create context
        self.context = Context(logger=logger,
                               web_access_logger=web_access_logger,
                               config=config,
                               args=ctx_args,
                               status=status)

        # Register the signal handlers
        signal.signal(signal.SIGTERM, self.signal)
        signal.signal(signal.SIGINT, self.signal)

        # Print context to log
        self.context.print_to_log()

        # Load the persists
        self.controller_persist_path = os.path.join(args.config_dir, Seedsync.__FILE_CONTROLLER_PERSIST)
        self.controller_persist = self._load_persist(ControllerPersist, self.controller_persist_path)

        self.auto_queue_persist_path = os.path.join(args.config_dir, Seedsync.__FILE_AUTO_QUEUE_PERSIST)
        self.auto_queue_persist = self._load_persist(AutoQueuePersist, self.auto_queue_persist_path)

    def run(self):
        self.context.logger.info("Starting seedsync")

        # Create controller
        controller = Controller(self.context, self.controller_persist)

        # Create auto queue
        auto_queue = AutoQueue(self.context, self.auto_queue_persist, controller)

        # Create web app
        web_app_builder = WebAppBuilder(self.context, controller, self.auto_queue_persist)
        web_app = web_app_builder.build()

        # Define child threads
        controller_job = ControllerJob(
            context=self.context.create_child_context(ControllerJob.__name__),
            controller=controller,
            auto_queue=auto_queue
        )
        webapp_job = WebAppJob(
            context=self.context.create_child_context(WebAppJob.__name__),
            web_app=web_app
        )

        do_start_controller = True

        # Initial checks to see if we should bother starting the controller
        if Seedsync._detect_incomplete_config(self.context.config):
            do_start_controller = False
            self.context.logger.error("Config is incomplete")
            self.context.status.server.up = False
            self.context.status.server.error_msg = Localization.Error.SETTINGS_INCOMPLETE

        # Start child threads here
        if do_start_controller:
            controller_job.start()
        webapp_job.start()

        try:
            prev_persist_timestamp = datetime.now()

            # Thread loop
            while True:
                # Persist to file occasionally
                now = datetime.now()
                if (now - prev_persist_timestamp).total_seconds() > Constants.MIN_PERSIST_TO_FILE_INTERVAL_IN_SECS:
                    prev_persist_timestamp = now
                    self.persist()

                # Propagate exceptions
                webapp_job.propagate_exception()
                # Catch controller exceptions and keep running, but notify the web server of the error
                try:
                    controller_job.propagate_exception()
                except AppError as exc:
                    self.context.status.server.up = False
                    self.context.status.server.error_msg = str(exc)
                    Seedsync.logger.exception("Caught exception")

                # Check if a restart is requested
                if web_app_builder.server_handler.is_restart_requested():
                    raise ServiceRestart()

                # Nothing else to do
                time.sleep(Constants.MAIN_THREAD_SLEEP_INTERVAL_IN_SECS)

        except Exception:
            self.context.logger.info("Exiting Seedsync")

            # This sleep is important to allow the jobs to finish setup before we terminate them
            # If we kill too early, the jobs may leave lingering threads around
            # Note: There might be a better way to ensure that job setup has completed, but this
            #       will do for now
            time.sleep(Constants.MAIN_THREAD_SLEEP_INTERVAL_IN_SECS)

            # Join all the threads here
            if do_start_controller:
                controller_job.terminate()
            webapp_job.terminate()

            # Wait for the threads to close
            if do_start_controller:
                controller_job.join()
            webapp_job.join()

            # Last persist
            self.persist()

            # Raise any exceptions so they can be logged properly
            # Note: ServiceRestart and ServiceExit will be caught and handled
            #       by outer code
            raise

    def persist(self):
        # Save the persists
        self.context.logger.debug("Persisting states to file")
        self.controller_persist.to_file(self.controller_persist_path)
        self.auto_queue_persist.to_file(self.auto_queue_persist_path)
        self.context.config.to_file(self.config_path)

    def signal(self, signum: int, _):
        # noinspection PyUnresolvedReferences
        # Signals is a generated enum
        self.context.logger.info("Caught signal {}".format(signal.Signals(signum).name))
        raise ServiceExit()

    @staticmethod
    def _parse_args():
        parser = argparse.ArgumentParser(description="Seedsync daemon")
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

        # Remove any existing handlers (needed when restarting)
        handlers = logger.handlers[:]
        for handler in handlers:
            handler.close()
            logger.removeHandler(handler)

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
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(name)s (%(processName)s/%(threadName)s) - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    @staticmethod
    def _create_default_config() -> Config:
        """
        Create a config with default values
        :return:
        """
        config = Config()

        config.general.debug = False

        config.lftp.remote_address = Seedsync.__CONFIG_DUMMY_VALUE
        config.lftp.remote_username = Seedsync.__CONFIG_DUMMY_VALUE
        config.lftp.remote_path = Seedsync.__CONFIG_DUMMY_VALUE
        config.lftp.local_path = Seedsync.__CONFIG_DUMMY_VALUE
        config.lftp.remote_path_to_scan_script = "/tmp/scanfs"
        config.lftp.num_max_parallel_downloads = 2
        config.lftp.num_max_parallel_files_per_download = 4
        config.lftp.num_max_connections_per_root_file = 4
        config.lftp.num_max_connections_per_dir_file = 4
        config.lftp.num_max_total_connections = 16

        config.controller.interval_ms_remote_scan = 30000
        config.controller.interval_ms_local_scan = 10000
        config.controller.interval_ms_downloading_scan = 1000

        config.web.port = 8800

        return config

    @staticmethod
    def _detect_incomplete_config(config: Config) -> bool:
        config_dict = config.as_dict()
        for sec_name in config_dict:
            for key in config_dict[sec_name]:
                if Seedsync.__CONFIG_DUMMY_VALUE == config_dict[sec_name][key]:
                    return True
        return False

    @staticmethod
    def _load_persist(cls: Type[T_Persist], file_path: str) -> T_Persist:
        """
        Loads a persist from file.
        Backs up existing persist if it's corrupted. Returns a new blank
        persist in its place.
        :param cls:
        :param file_path:
        :return:
        """
        if os.path.isfile(file_path):
            try:
                return cls.from_file(file_path)
            except PersistError:
                if Seedsync.logger:
                    Seedsync.logger.exception("Caught exception")

                # backup file
                Seedsync.__backup_file(file_path)

                # noinspection PyCallingNonCallable
                return cls()
        else:
            # noinspection PyCallingNonCallable
            return cls()

    @staticmethod
    def __backup_file(file_path: str):
        file_name = os.path.basename(file_path)
        file_dir = os.path.dirname(file_path)
        i = 1
        while True:
            backup_path = os.path.join(
                file_dir, "{}.{}.bak".format(file_name, i)
            )
            if not os.path.exists(backup_path):
                break
            i += 1
        if Seedsync.logger:
            Seedsync.logger.info("Backing up {} to {}".format(file_path, backup_path))
        shutil.copy(file_path, backup_path)


if __name__ == "__main__":
    if sys.hexversion < 0x03050000:
        sys.exit("Python 3.5 or newer is required to run this program.")

    while True:
        try:
            seedsync = Seedsync()
            seedsync.run()
        except ServiceExit:
            break
        except ServiceRestart:
            Seedsync.logger.info("Restarting...")
            continue
        except Exception as e:
            Seedsync.logger.exception("Caught exception")
            raise

        Seedsync.logger.info("Exited successfully")
