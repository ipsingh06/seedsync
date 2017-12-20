# Copyright 2017, Inderpreet Singh, All rights reserved.


# my libs
from common import overrides, Job, Context
from .controller import Controller
from .auto_queue import AutoQueue


class ControllerJob(Job):
    """
    The controller service
    Handles querying and downloading of files
    """
    def __init__(self,
                 context: Context,
                 controller: Controller,
                 auto_queue: AutoQueue):
        super().__init__(name=self.__class__.__name__, context=context)
        self.__controller = controller
        self.__auto_queue = auto_queue

    @overrides(Job)
    def setup(self):
        self.__controller.start()

    @overrides(Job)
    def execute(self):
        self.__controller.process()
        self.__auto_queue.process()

    @overrides(Job)
    def cleanup(self):
        self.__controller.exit()
