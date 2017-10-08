# Copyright 2017, Inderpreet Singh, All rights reserved.

import os
import logging
from typing import List, Optional, Set

# my libs
from system import SystemFile
from lftp import LftpJobStatus
from model import ModelFile, Model, ModelError


class ModelBuilder:
    """
    ModelBuilder combines all the difference sources of file system info
    to build a model. These sources include:
      * downloading file system as a Dict[name, SystemFile]
      * local file system as a Dict[name, SystemFile]
      * remote file system as a Dict[name, SystemFile]
      * lftp status as Dict[name, LftpJobStatus]
    """
    def __init__(self):
        self.logger = logging.getLogger("ModelBuilder")
        self.__downloading_files = dict()
        self.__local_files = dict()
        self.__remote_files = dict()
        self.__lftp_statuses = dict()
        self.__downloaded_files = set()

    def set_base_logger(self, base_logger: logging.Logger):
        self.logger = base_logger.getChild("ModelBuilder")

    def set_downloading_files(self, downloading_files: List[SystemFile]):
        self.__downloading_files = {file.name: file for file in downloading_files}

    def set_local_files(self, local_files: List[SystemFile]):
        self.__local_files = {file.name: file for file in local_files}

    def set_remote_files(self, remote_files: List[SystemFile]):
        self.__remote_files = {file.name: file for file in remote_files}

    def set_lftp_statuses(self, lftp_statuses: List[LftpJobStatus]):
        self.__lftp_statuses = {file.name: file for file in lftp_statuses}

    def set_downloaded_files(self, downloaded_files: Set[str]):
        self.__downloaded_files = downloaded_files

    def clear(self):
        self.__local_files = dict()
        self.__remote_files = dict()
        self.__lftp_statuses = dict()

    def build_model(self) -> Model:
        model = Model()
        model.set_base_logger(logging.getLogger("dummy"))  # ignore the logs for this temp model
        all_file_names = set().union(self.__local_files.keys(),
                                     self.__remote_files.keys(),
                                     self.__lftp_statuses.keys())
        for name in all_file_names:
            remote = self.__remote_files.get(name, None)
            # use downloading file if it exists, otherwise local
            local = self.__downloading_files.get(name, None) or self.__local_files.get(name, None)
            status = self.__lftp_statuses.get(name, None)

            if remote is None and local is None and status is None:
                # this should never happen, but just in case
                raise ModelError("Zero sources have a file object")

            # sanity check between the sources
            is_dir = remote.is_dir if remote else local.is_dir if local else status.type == LftpJobStatus.Type.MIRROR
            if (remote and is_dir != remote.is_dir) or \
               (local and is_dir != local.is_dir) or \
               (status and is_dir != (status.type == LftpJobStatus.Type.MIRROR)):
                raise ModelError("Mismatch in is_dir between sources")

            def __fill_model_file(_model_file: ModelFile,
                                  _remote: Optional[SystemFile],
                                  _local: Optional[SystemFile],
                                  _transfer_state: Optional[LftpJobStatus.TransferState]):
                # set local and remote sizes
                if _remote:
                    _model_file.remote_size = _remote.size
                if _local:
                    _model_file.local_size = _local.size

                # Note: no longer use lftp's file sizes
                #       they represent remaining size for resumed downloads

                # set the downloading speed and eta
                if _transfer_state:
                    _model_file.downloading_speed = _transfer_state.speed
                    _model_file.eta = _transfer_state.eta

            model_file = ModelFile(name, is_dir)
            # set the file state
            # for now we only set to Queued or Downloading
            # later after all children are built, we can set to Downloaded after performing a check
            if status:
                model_file.state = ModelFile.State.QUEUED if status.state == LftpJobStatus.State.QUEUED \
                                   else ModelFile.State.DOWNLOADING
            # fill the rest
            __fill_model_file(model_file,
                              remote,
                              local,
                              status.total_transfer_state if status and status.state == LftpJobStatus.State.RUNNING
                              else None)

            # Traverse SystemFile children tree in BFS order
            # Store (remote, local, status, model_file) tuple in traversal frontier where remote and local
            # correspond to the same node in both remote and local SystemFile trees, status corresponds
            # to the LFTP status for the entire tree, and model_file corresponds to the generated ModelFile
            # for the pair
            # Note: in this case the frontier contains nodes that have already been process, it is
            #       merely used for traversing children
            frontier = []
            if remote or local:
                frontier.append((remote, local, status, model_file))
            while frontier:
                _remote, _local, _status, _model_file = frontier.pop(0)
                _remote_children = {sf.name: sf for sf in _remote.children} if _remote else {}
                _local_children = {sf.name: sf for sf in _local.children} if _local else {}
                _all_children_names = set().union(_remote_children.keys(), _local_children.keys())
                for _child_name in _all_children_names:
                    _remote_child = _remote_children.get(_child_name, None)
                    _local_child = _local_children.get(_child_name, None)
                    _is_dir = _remote_child.is_dir if _remote_child else _local_child.is_dir
                    # sanity check is_dir
                    if (_remote_child and _is_dir != _remote_child.is_dir) or \
                       (_local_child and _is_dir != _local_child.is_dir):
                        raise ModelError("Mismatch in is_dir between child sources")
                    _child_model_file = ModelFile(_child_name, _is_dir)

                    # add it to the parent right away so we can access the full path
                    _model_file.add_child(_child_model_file)

                    # find the transfer state (if it exists) corresponding to this child
                    # Note: transfer states are in full paths
                    # Note2: transfer states don't include root path
                    _child_status_path = os.path.join(*(_child_model_file.full_path.split(os.sep)[1:]))
                    _child_transfer_state = None
                    if _status:
                        _child_transfer_state = next((ts for n, ts in _status.get_active_file_transfer_states()
                                                     if n == _child_status_path), None)
                    # Set the state, first matching criteria below decides state
                    #   child is a directory: Default
                    #   child is active: Downloading
                    #   child local_size >= remote_size: Downloaded
                    #   remote child exists and root is Queued or Downloading: Queued
                    #   Default
                    # Result:
                    #   subdirectories are always Default
                    #   downloading files are Downloading
                    #   finished files are Downloaded
                    #   Queued and Downloading root's unfinished files are Queued
                    #   Local-only files are Default
                    if _is_dir:
                        _child_model_file.state = ModelFile.State.DEFAULT
                    elif _child_transfer_state:
                        _child_model_file.state = ModelFile.State.DOWNLOADING
                    elif _remote_child and _local_child and _local_child.size >= _remote_child.size:
                        _child_model_file.state = ModelFile.State.DOWNLOADED
                    elif _remote_child and model_file.state in (ModelFile.State.QUEUED, ModelFile.State.DOWNLOADING):
                        _child_model_file.state = ModelFile.State.QUEUED
                    else:
                        _child_model_file.state = ModelFile.State.DEFAULT

                    # fill the rest
                    __fill_model_file(_child_model_file,
                                      _remote_child,
                                      _local_child,
                                      _child_transfer_state)
                    # add child to frontier
                    frontier.append((_remote_child, _local_child, _status, _child_model_file))

            # now we can determine if root is Downloaded
            # root is Downloaded if all child remote files are Downloaded
            # again we use BFS to traverse
            if model_file.state == ModelFile.State.DEFAULT:
                if not model_file.is_dir and \
                        model_file.local_size is not None and \
                        model_file.remote_size is not None and \
                        model_file.local_size >= model_file.remote_size:
                    # root is a finished single file
                    model_file.state = ModelFile.State.DOWNLOADED
                elif model_file.is_dir and model_file.remote_size is not None:
                    # root is a directory that also exists remotely
                    # check all the children
                    all_downloaded = True
                    frontier = []
                    frontier += model_file.get_children()
                    while frontier:
                        _child_file = frontier.pop(0)
                        if not _child_file.is_dir and \
                                _child_file.remote_size is not None and \
                                _child_file.state != ModelFile.State.DOWNLOADED:
                            all_downloaded = False
                            break
                        frontier += _child_file.get_children()
                    if all_downloaded:
                        model_file.state = ModelFile.State.DOWNLOADED

            # next we determine if root was Deleted
            # root is Deleted if it does not exist locally, but was downloaded in the past
            if model_file.state == ModelFile.State.DEFAULT and \
                    model_file.local_size is None and \
                    model_file.name in self.__downloaded_files:
                model_file.state = ModelFile.State.DELETED

            model.add_file(model_file)

        return model
