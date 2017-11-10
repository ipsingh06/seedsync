# Copyright 2017, Inderpreet Singh, All rights reserved.


class Localization:
    class Error:
        MISSING_FILE = "The file '{}' doesn't exist."
        REMOTE_SERVER_SCAN = "An error occurred while scanning the remote server."
        REMOTE_SERVER_INSTALL = "An error occurred while installing scanner script to remote server."
        LOCAL_SERVER_SCAN = "An error occurred while scanning the local system."
        SETTINGS_INCOMPLETE = "The settings are not fully configured."
