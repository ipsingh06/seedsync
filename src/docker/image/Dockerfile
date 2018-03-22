ARG SEEDSYNC_VERSION

FROM seedsync:$SEEDSYNC_VERSION


# Replace settings
RUN \
    sed -i 's/debug = False/debug = True/' /config/settings.cfg && \
    grep -q 'debug = True' /config/settings.cfg
RUN \
    sed -i 's/verbose = False/verbose = True/' /config/settings.cfg && \
    grep -q 'verbose = True' /config/settings.cfg
RUN \
    sed -i 's/remote_address = <replace me>/remote_address = remote/' /config/settings.cfg && \
    grep -q 'remote_address = remote' /config/settings.cfg
RUN \
    sed -i 's/remote_username = <replace me>/remote_username = remoteuser/' /config/settings.cfg && \
    grep -q 'remote_username = remoteuser' /config/settings.cfg
RUN \
    sed -i 's/remote_password = <replace me>/remote_password = remotepass/' /config/settings.cfg && \
    grep -q 'remote_password = remotepass' /config/settings.cfg
RUN \
    sed -i 's/remote_port = 22/remote_port = 1234/' /config/settings.cfg && \
    grep -q 'remote_port = 1234' /config/settings.cfg
RUN \
    sed -i 's/remote_path = <replace me>/remote_path = \/home\/remoteuser\/files/' /config/settings.cfg && \
    grep -q 'remote_path = \/home\/remoteuser\/files' /config/settings.cfg
RUN \
    sed -i 's/patterns_only = False/patterns_only = True/' /config/settings.cfg && \
    grep -q 'patterns_only = True' /config/settings.cfg
