# Copyright 2017, Inderpreet Singh, All rights reserved.

import os
import logging
from typing import List, Optional

# my libs
from system import SystemFile
from lftp import LftpJobStatus
from model import ModelFile, Model, ModelError


class ModelBuilder:
    """
    ModelBuilder combines all the difference sources of file system info
    to build a model. These sources include:
      * local file system as a Dict[name, SystemFile]
      * remote file system as a Dict[name, SystemFile]
      * lftp status as Dict[name, LftpJobStatus]
    """
    def __init__(self):
        self.logger = logging.getLogger("ModelBuilder")
        self.__local_files = dict()
        self.__remote_files = dict()
        self.__lftp_statuses = dict()

    def set_base_logger(self, base_logger: logging.Logger):
        self.logger = base_logger.getChild("ModelBuilder")

    def set_local_files(self, local_files: List[SystemFile]):
        self.__local_files = {file.name: file for file in local_files}

    def set_remote_files(self, remote_files: List[SystemFile]):
        self.__remote_files = {file.name: file for file in remote_files}

    def set_lftp_statuses(self, lftp_statuses: List[LftpJobStatus]):
        self.__lftp_statuses = {file.name: file for file in lftp_statuses}

    def clear(self):
        self.__local_files = dict()
        self.__remote_files = dict()
        self.__lftp_statuses = dict()

    def build_model(self) -> Model:
        model = Model()
        model.set_base_logger(self.logger)
        all_file_names = set().union(self.__local_files.keys(),
                                     self.__remote_files.keys(),
                                     self.__lftp_statuses.keys())
        for name in all_file_names:
            remote = self.__remote_files.get(name, None)
            local = self.__local_files.get(name, None)
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

                # overwrite sizes with status info
                if _transfer_state:
                    if _transfer_state.size_local:
                        _model_file.local_size = _transfer_state.size_local
                    elif _transfer_state.size_remote and _transfer_state.percent_local:
                        # estimate the local size
                        _model_file.local_size = int(float(_transfer_state.size_remote) *
                                                     _transfer_state.percent_local)
                    if _transfer_state.size_remote:
                        _model_file.remote_size = _transfer_state.size_remote
                    # we won't try and estimate the remote size since it's unlikely to change often

                # set the downloading speed and eta
                if _transfer_state:
                    _model_file.downloading_speed = _transfer_state.speed
                    _model_file.eta = _transfer_state.eta

            model_file = ModelFile(name, is_dir)
            # set the file state
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
                    #   child is active: Downloading
                    #                    Note: only files can be active, not dirs
                    #   child remote size <= local size: Default
                    #   local exists but not remote: Default
                    #   parent is downloading: Queued
                    #   use parent state
                    # Result:
                    #   Default and Queued root's children are same state (there's no status object)
                    #   Downloading root's dirs are Default if completed, else Queued
                    #   Downloading files can be Default, Queued, or Downloading
                    #   Any files on only local will always be Default
                    if _child_transfer_state:
                        _child_model_file.state = ModelFile.State.DOWNLOADING
                    elif _remote_child and _local_child and _remote_child.size <= _local_child.size:
                        _child_model_file.state = ModelFile.State.DEFAULT
                    elif _local_child and not _remote_child:
                        _child_model_file.state = ModelFile.State.DEFAULT
                    elif _model_file.state == ModelFile.State.DOWNLOADING:
                        _child_model_file.state = ModelFile.State.QUEUED
                    else:
                        _child_model_file.state = _model_file.state

                    # fill the rest
                    __fill_model_file(_child_model_file,
                                      _remote_child,
                                      _local_child,
                                      _child_transfer_state)
                    # add child to frontier
                    frontier.append((_remote_child, _local_child, _status, _child_model_file))

            model.add_file(model_file)
        return model
