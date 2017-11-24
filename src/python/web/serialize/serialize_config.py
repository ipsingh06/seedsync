# Copyright 2017, Inderpreet Singh, All rights reserved.

import json
import collections

from common import PylftpConfig


class SerializeConfig:
    @staticmethod
    def config(config: PylftpConfig) -> str:
        config_dict = config.as_dict()

        # Make the section names lower case
        keys = list(config_dict.keys())
        config_dict_lowercase = collections.OrderedDict()
        for key in keys:
            config_dict_lowercase[key.lower()] = config_dict[key]

        return json.dumps(config_dict_lowercase)
