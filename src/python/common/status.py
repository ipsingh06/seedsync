# Copyright 2017, Inderpreet Singh, All rights reserved.

from abc import ABC, abstractmethod
from typing import Any, TypeVar, Type
from threading import Lock

from common import overrides


T = TypeVar('T', bound='StatusComponent')


class IStatusComponentListener(ABC):
    @abstractmethod
    def notify(self, name: str):
        """
        Called when a property is changed
        :param name:
        :return:
        """
        pass


class BaseStatus:
    """
    Provides functionality to dynamically create properties
    """

    # noinspection PyProtectedMember
    @classmethod
    def _create_property(cls, name: str) -> property:
        return property(fget=lambda s: s._get_property(name),
                        fset=lambda s, v: s._set_property(name, v))

    def _get_property(self, name: str) -> Any:
        return getattr(self, "__" + name, None)

    def _set_property(self, name: str, value: Any):
        setattr(self, "__" + name, value)


class StatusComponent(BaseStatus):
    """
    Base class for status of a single component
    """

    def __init__(self):
        self.__listeners = []
        self.__properties = []  # names of properties created

    def add_listener(self, listener: IStatusComponentListener):
        if listener not in self.__listeners:
            self.__listeners.append(listener)

    def remove_listener(self, listener: IStatusComponentListener):
        if listener in self.__listeners:
            self.__listeners.remove(listener)

    @classmethod
    def copy(cls: Type[T], src: T, dst: T) -> None:
        property_names = [p for p in dir(cls) if isinstance(getattr(cls, p), property)]
        for prop in property_names:
            setattr(dst, "__" + prop, getattr(src, "__" + prop))

    @overrides(BaseStatus)
    def _set_property(self, name: str, value: Any):
        super()._set_property(name, value)
        # Notify listeners
        for listener in self.__listeners:
            listener.notify(name)


class IStatusListener(ABC):
    @abstractmethod
    def notify(self):
        """
        Called when any property of a component is changed
        :return:
        """
        pass


class Status(BaseStatus):
    """
    This class tracks the status of all components across the server
    This is meant to be one-way communication - i.e. only one component
    should set the status

    Clients can use listeners to be notified when values are updated.
    Listeners can be added to the overall status for notification on
    any change, or to each component for component-specific changes.
    """

    class CompListener(IStatusComponentListener):
        """Propagates notifications from component to status listeners"""
        def __init__(self, status: "Status"):
            self.status = status

        def notify(self, name: str):
            self.status._listeners_lock.acquire()
            for listener in self.status._listeners:
                listener.notify()
            self.status._listeners_lock.release()

    # ----- Start of component definition -----
    class ServerStatus(StatusComponent):
        up = StatusComponent._create_property("up")
        error_msg = StatusComponent._create_property("error_msg")

        def __init__(self):
            super().__init__()
            self.up = True
            self.error_msg = None

    # ----- End of component definition -----

    # Component registration
    server = BaseStatus._create_property("server")

    def __init__(self):
        self._listeners = []
        self._listeners_lock = Lock()
        self.__comp_listener = Status.CompListener(self)

        # Component initialization
        self.server = self.__create_component(Status.ServerStatus)

    def copy(self) -> "Status":
        copy = Status()
        cls = Status
        property_names = [p for p in dir(cls) if isinstance(getattr(cls, p), property)]
        for prop in property_names:
            src_comp = self._get_property(prop)
            dst_comp = copy._get_property(prop)
            src_comp.__class__.copy(src_comp, dst_comp)
        return copy

    def add_listener(self, listener: IStatusListener):
        self._listeners_lock.acquire()
        if listener not in self._listeners:
            self._listeners.append(listener)
        self._listeners_lock.release()

    def remove_listener(self, listener: IStatusListener):
        self._listeners_lock.acquire()
        if listener in self._listeners:
            self._listeners.remove(listener)
        self._listeners_lock.release()

    def __create_component(self, comp_cls: Type[T]) -> T:
        """Create a component and register our listener with it"""
        # PyCharm is confused and complains about the ctor
        # noinspection PyCallingNonCallable
        comp = comp_cls()
        comp.add_listener(self.__comp_listener)
        return comp

    @overrides(BaseStatus)
    def _set_property(self, name: str, value: Any):
        """Override set property so that it can only be set once"""
        if self._get_property(name) is not None:
            raise ValueError("Cannot reassign component")
        super()._set_property(name, value)
