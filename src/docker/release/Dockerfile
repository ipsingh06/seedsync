FROM ubuntu:16.04

# Install dependencies
RUN apt-get update && apt-get install -y \
    libssl-dev \
    lftp \
    openssh-client \
    rar \
    unrar \
    p7zip

# Disable the known hosts prompt
RUN mkdir -p /root/.ssh && echo "StrictHostKeyChecking no\nUserKnownHostsFile /dev/null" > /root/.ssh/config

COPY artifacts /app

RUN mkdir /config /config/log
RUN mkdir /downloads

# Generate default config
RUN /app/seedsync -c /config --exit 2>/dev/null; exit 0

# Replace default values
RUN \
    sed -i 's/local_path = <replace me>/local_path = \/downloads\//' /config/settings.cfg && \
    grep -q 'local_path = \/downloads\/' /config/settings.cfg

# Must run app inside shell
# Otherwise the container crashes as soon as a child process exits
CMD [ \
    "/bin/sh", "-c", \
    "/app/seedsync -c /config" \
]

EXPOSE 8800
