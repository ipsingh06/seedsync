FROM ubuntu:16.04

# Install dependencies
RUN apt-get update && apt-get install -y \
    libssl-dev \
    lftp \
    openssh-client \
    rar \
    unrar \
    p7zip \
    python3-pip

# Disable the known hosts prompt
RUN mkdir -p /root/.ssh && echo "StrictHostKeyChecking no\nUserKnownHostsFile /dev/null" > /root/.ssh/config

RUN mkdir /app
COPY python /app/python
COPY html /app/html
COPY scanfs /app/scanfs

RUN mkdir /config /config/log
RUN mkdir /downloads

RUN pip3 install --upgrade pip
RUN pip3 install -r /app/python/requirements.txt

# First time config setup and replacement
ADD setup_default_config.sh /scripts/
RUN /scripts/setup_default_config.sh

# Must run app inside shell
# Otherwise the container crashes as soon as a child process exits
CMD [ \
    "python3.5", \
    "/app/python/seedsync.py", \
    "-c", "/config", \
    "--html", "/app/html", \
    "--scanfs", "/app/scanfs" \
]

EXPOSE 8800
