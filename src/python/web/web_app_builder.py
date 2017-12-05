# Copyright 2017, Inderpreet Singh, All rights reserved.

from common import PylftpContext
from controller import Controller, AutoQueuePersist
from .web_app import WebApp
from .handler.stream_model import ModelStreamHandler
from .handler.stream_status import StatusStreamHandler
from .handler.controller import ControllerHandler
from .handler.server import ServerHandler
from .handler.config import ConfigHandler
from .handler.auto_queue import AutoQueueHandler


class WebAppBuilder:
    """
    Helper class to build WebApp with all the extensions
    """
    def __init__(self,
                 context: PylftpContext,
                 controller: Controller,
                 auto_queue_persist: AutoQueuePersist):
        self.__context = context
        self.__controller = controller

        self.controller_handler = ControllerHandler(controller)
        self.server_handler = ServerHandler(context)
        self.config_handler = ConfigHandler(context.config)
        self.auto_queue_handler = AutoQueueHandler(auto_queue_persist)

    def build(self) -> WebApp:
        web_app = WebApp(context=self.__context,
                         controller=self.__controller)

        ModelStreamHandler.register(web_app=web_app,
                                    controller=self.__controller)

        StatusStreamHandler.register(web_app=web_app,
                                     status=self.__context.status)

        self.controller_handler.add_routes(web_app)
        self.server_handler.add_routes(web_app)
        self.config_handler.add_routes(web_app)
        self.auto_queue_handler.add_routes(web_app)

        web_app.add_default_routes()

        return web_app
