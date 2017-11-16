# Copyright 2017, Inderpreet Singh, All rights reserved.

from bottle import HTTPResponse

from common import PylftpContext, overrides
from ..web_app import IHandler, WebApp


class ServerHandler(IHandler):
    def __init__(self, context: PylftpContext):
        self.logger = context.logger.getChild("ServerActionHandler")
        self.__request_restart = False

    @overrides(IHandler)
    def add_routes(self, web_app: WebApp):
        web_app.add_handler("/server/command/restart", self.__handle_action_restart)

    def is_restart_requested(self):
        """
        Returns true is a restart is requested
        :return:
        """
        return self.__request_restart

    def __handle_action_restart(self):
        """
        Request a server restart
        :return:
        """
        self.logger.info("Received a restart action")
        self.__request_restart = True
        return HTTPResponse(body="Requested restart")
