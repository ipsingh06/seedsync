# Copyright 2017, Inderpreet Singh, All rights reserved.

import unittest
from unittest.mock import MagicMock
import logging
import sys

from webtest import TestApp

from common import overrides, Status, PylftpConfig
from controller import AutoQueuePersist
from web import WebAppBuilder


class BaseTestWebApp(unittest.TestCase):
    """
    Base class for testing web app
    Sets up the web app with mocks
    """
    @overrides(unittest.TestCase)
    def setUp(self):
        self.context = MagicMock()
        self.controller = MagicMock()

        # Mock the base logger
        logger = logging.getLogger()
        handler = logging.StreamHandler(sys.stdout)
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")
        handler.setFormatter(formatter)
        self.context.logger = logger

        # Model files
        self.model_files = []

        # Real status
        self.context.status = Status()

        # Real config
        self.context.config = PylftpConfig()

        # Real auto-queue persist
        self.auto_queue_persist = AutoQueuePersist()

        # Capture the model listener
        def capture_listener(listener):
            self.model_listener = listener
            return self.model_files
        self.model_listener = None
        self.controller.get_model_files_and_add_listener = MagicMock()
        self.controller.get_model_files_and_add_listener.side_effect = capture_listener
        self.controller.remove_model_listener = MagicMock()

        # noinspection PyTypeChecker
        self.web_app_builder = WebAppBuilder(self.context,
                                             self.controller,
                                             self.auto_queue_persist)
        self.web_app = self.web_app_builder.build()
        self.test_app = TestApp(self.web_app)


class TestWebApp(BaseTestWebApp):
    def test_process(self):
        self.web_app.process()
