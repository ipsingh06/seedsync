# Copyright 2017, Inderpreet Singh, All rights reserved.


class Constants:
    """
    POD class to hold shared constants
    :return:
    """
    SERVICE_NAME = "pylftp"
    MAIN_THREAD_SLEEP_INTERVAL_IN_SECS = 0.5
    MAX_LOG_SIZE_IN_BYTES = 10*1024*1024  # 10 MB
    LOG_BACKUP_COUNT = 10
    WEB_ACCESS_LOG_NAME = 'web_access'
    MIN_PERSIST_TO_FILE_INTERVAL_IN_SECS = 30
    JSON_PRETTY_PRINT_INDENT = 4
