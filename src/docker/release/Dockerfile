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

ADD setup_default_config.sh /scripts/
RUN /scripts/setup_default_config.sh

# Must run app inside shell
# Otherwise the container crashes as soon as a child process exits
CMD [ \
    "/bin/sh", "-c", \
    "/app/seedsync -c /config" \
]

EXPOSE 8800
