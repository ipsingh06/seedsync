# Copyright 2017, Inderpreet Singh, All rights reserved.

from datetime import datetime
from enum import Enum
from typing import Optional, List
import copy
import os


class ModelFile:
    """
    Represents a file or directory
    The information in this object may be inconsistent. E.g. the size of a directory
    may not match the sum of its children. This is allowed as a source may have
    updated only certain levels in the hierarchy. Specifically for this example,
    an Lftp status provides local sizes for a downloading directory but not its
    children.
    """
    class State(Enum):
        DEFAULT = 0
        DOWNLOADING = 1
        QUEUED = 2
        DOWNLOADED = 3
        DELETED = 4
        EXTRACTING = 5
        EXTRACTED = 6

    def __init__(self, name: str, is_dir: bool):
        self.__name = name  # file or folder name
        self.__is_dir = is_dir  # True if this is a dir, False if file
        self.__state = ModelFile.State.DEFAULT  # status
        self.__remote_size = None  # remote size in bytes, None if file does not exist
        self.__local_size = None  # local size in bytes, None if file does not exist
        self.__transferred_size = None  # transferred size in bytes, None if file does not exist
        self.__downloading_speed = None  # in bytes / sec, None if not downloading
        self.__eta = None  # est. time remaining in seconds, None if not available
        self.__is_extractable = False  # whether file is an archive or dir contains archives
        self.__local_created_timestamp = None
        self.__local_modified_timestamp = None
        self.__remote_created_timestamp = None
        self.__remote_modified_timestamp = None
        # timestamp of the latest update
        # Note: timestamp is not part of equality operator
        self.__update_timestamp = datetime.now()
        self.__children = []  # children files
        self.__parent = None  # direct predecessor

    def __eq__(self, other):
        # disregard in comparisons:
        #   timestamp: we don't care about it
        #   parent: semantics are to check self and children only
        #   children: check these manually for easier debugging
        ka = set(self.__dict__).difference({
            "_ModelFile__update_timestamp",
            "_ModelFile__parent",
            "_ModelFile__children"
        })
        kb = set(other.__dict__).difference({
            "_ModelFile__update_timestamp",
            "_ModelFile__parent",
            "_ModelFile__children"
        })
        # Check self properties
        if ka != kb:
            return False
        if not all(self.__dict__[k] == other.__dict__[k] for k in ka):
            return False

        # Check children's properties
        if len(self.__children) != len(other.__children):
            return False
        my_children_dict = {f.name: f for f in self.__children}
        other_children_dict = {f.name: f for f in other.__children}
        if my_children_dict.keys() != other_children_dict.keys():
            return False
        for name in my_children_dict.keys():
            if my_children_dict[name] != other_children_dict[name]:
                return False

        return True

    def __repr__(self):
        return str(self.__dict__)

    @property
    def name(self) -> str: return self.__name

    @property
    def is_dir(self) -> bool: return self.__is_dir

    @property
    def state(self) -> State: return self.__state

    @state.setter
    def state(self, state: State):
        if type(state) != ModelFile.State:
            raise TypeError
        self.__state = state

    @property
    def remote_size(self) -> Optional[int]: return self.__remote_size

    @remote_size.setter
    def remote_size(self, remote_size: Optional[int]):
        if type(remote_size) == int:
            if remote_size < 0:
                raise ValueError
            self.__remote_size = remote_size
        elif remote_size is None:
            self.__remote_size = remote_size
        else:
            raise TypeError

    @property
    def local_size(self) -> Optional[int]: return self.__local_size

    @local_size.setter
    def local_size(self, local_size: Optional[int]):
        if type(local_size) == int:
            if local_size < 0:
                raise ValueError
            self.__local_size = local_size
        elif local_size is None:
            self.__local_size = local_size
        else:
            raise TypeError

    @property
    def transferred_size(self) -> Optional[int]: return self.__transferred_size

    @transferred_size.setter
    def transferred_size(self, transferred_size: Optional[int]):
        if type(transferred_size) == int:
            if transferred_size < 0:
                raise ValueError
            self.__transferred_size = transferred_size
        elif transferred_size is None:
            self.__transferred_size = transferred_size
        else:
            raise TypeError

    @property
    def downloading_speed(self) -> Optional[int]: return self.__downloading_speed

    @downloading_speed.setter
    def downloading_speed(self, downloading_speed: Optional[int]):
        if type(downloading_speed) == int:
            if downloading_speed < 0:
                raise ValueError
            self.__downloading_speed = downloading_speed
        elif downloading_speed is None:
            self.__downloading_speed = downloading_speed
        else:
            raise TypeError

    @property
    def update_timestamp(self) -> datetime: return self.__update_timestamp

    @update_timestamp.setter
    def update_timestamp(self, update_timestamp: datetime):
        if type(update_timestamp) != datetime:
            raise TypeError
        self.__update_timestamp = update_timestamp

    @property
    def eta(self) -> Optional[int]: return self.__eta

    @eta.setter
    def eta(self, eta: Optional[int]):
        if type(eta) == int:
            if eta < 0:
                raise ValueError
            self.__eta = eta
        elif eta is None:
            self.__eta = eta
        else:
            raise TypeError

    @property
    def is_extractable(self) -> bool: return self.__is_extractable

    @is_extractable.setter
    def is_extractable(self, is_extractable: bool):
        self.__is_extractable = is_extractable

    @property
    def local_created_timestamp(self) -> datetime: return self.__local_created_timestamp

    @local_created_timestamp.setter
    def local_created_timestamp(self, local_created_timestamp: datetime):
        if type(local_created_timestamp) != datetime:
            raise TypeError
        self.__local_created_timestamp = local_created_timestamp

    @property
    def local_modified_timestamp(self) -> datetime: return self.__local_modified_timestamp

    @local_modified_timestamp.setter
    def local_modified_timestamp(self, local_modified_timestamp: datetime):
        if type(local_modified_timestamp) != datetime:
            raise TypeError
        self.__local_modified_timestamp = local_modified_timestamp

    @property
    def remote_created_timestamp(self) -> datetime: return self.__remote_created_timestamp

    @remote_created_timestamp.setter
    def remote_created_timestamp(self, remote_created_timestamp: datetime):
        if type(remote_created_timestamp) != datetime:
            raise TypeError
        self.__remote_created_timestamp = remote_created_timestamp

    @property
    def remote_modified_timestamp(self) -> datetime: return self.__remote_modified_timestamp

    @remote_modified_timestamp.setter
    def remote_modified_timestamp(self, remote_modified_timestamp: datetime):
        if type(remote_modified_timestamp) != datetime:
            raise TypeError
        self.__remote_modified_timestamp = remote_modified_timestamp

    @property
    def full_path(self) -> str:
        """Full path including all predecessors"""
        if self.__parent:
            return os.path.join(self.__parent.full_path, self.name)
        return self.name

    def add_child(self, child_file: "ModelFile"):
        if not self.is_dir:
            raise TypeError("Cannot add child to a non-directory")
        if child_file is self:
            raise ValueError("Cannot add parent as a child")
        if child_file.name in (f.name for f in self.__children):
            raise ValueError("Cannot add child more than once")
        self.__children.append(child_file)
        child_file.__parent = self

    def get_children(self) -> List["ModelFile"]:
        return copy.copy(self.__children)

    @property
    def parent(self) -> Optional["ModelFile"]:
        return self.__parent
