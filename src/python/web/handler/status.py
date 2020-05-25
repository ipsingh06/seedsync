# Copyright 2017, Inderpreet Singh, All rights reserved.

from bottle import HTTPResponse

from common import Status, overrides
from ..web_app import IHandler, WebApp
from ..serialize import SerializeStatusJson


class StatusHandler(IHandler):
    def __init__(self, status: Status):
        self.__status = status

    @overrides(IHandler)
    def add_routes(self, web_app: WebApp):
        web_app.add_handler("/server/status", self.__handle_get_status)

    def __handle_get_status(self):
        out_json = SerializeStatusJson.status(self.__status)
        return HTTPResponse(body=out_json)
