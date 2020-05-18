FROM ubuntu:18.04 as seedsync_docker_image

# Install dependencies
RUN apt-get update && apt-get install -y \
    libssl-dev \
    lftp \
    openssh-client \
    rar \
    unrar \
    p7zip \
    python3.7 \
    python3.7-dev \
    python3.7-distutils \
    curl

# Switch to Python 3.7
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.7 1
RUN update-alternatives --set python /usr/bin/python3.7
RUN curl -s https://bootstrap.pypa.io/get-pip.py -o get-pip.py && \
    python get-pip.py --force-reinstall && \
    rm get-pip.py

RUN apt-get install -y python3-pip
RUN pip3 --version

RUN pip3 install pipenv
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8
RUN pipenv --version

# Disable the known hosts prompt
RUN mkdir -p /root/.ssh && echo "StrictHostKeyChecking no\nUserKnownHostsFile /dev/null" > /root/.ssh/config

RUN mkdir /app
COPY src/python /app/python
COPY --from=seedsync/build/html /html /app/html
COPY --from=seedsync/build/scanfs /scanfs /app/scanfs
COPY src/docker/build/docker-image/setup_default_config.sh /scripts/

RUN cd /app/python && pipenv install --system --deploy

# Create non-root user and directories under that user
RUN groupadd -g 1000 seedsync && \
    useradd -r -u 1000 -g seedsync seedsync
RUN mkdir /config && \
    mkdir /downloads && \
    chown seedsync:seedsync /config && \
    chown seedsync:seedsync /downloads

# Switch to non-root user
USER seedsync

# First time config setup and replacement
RUN /scripts/setup_default_config.sh

# Must run app inside shell
# Otherwise the container crashes as soon as a child process exits
CMD [ \
    "python", \
    "/app/python/seedsync.py", \
    "-c", "/config", \
    "--html", "/app/html", \
    "--scanfs", "/app/scanfs" \
]

EXPOSE 8800
