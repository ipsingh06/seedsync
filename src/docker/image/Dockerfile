ARG SEEDSYNC_VERSION

FROM seedsync:$SEEDSYNC_VERSION

WORKDIR /scripts
ADD setup_seedsync.sh /scripts/
RUN /scripts/setup_seedsync.sh
