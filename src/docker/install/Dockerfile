ARG BASE_IMAGE=ubuntu:16.04

FROM $BASE_IMAGE

# Install dependencies
RUN apt-get update && apt-get install -y \
    sudo \
    libssl-dev \
    libexpat1 \
    expect \
    lftp \
    openssh-client

# Create non-root user
RUN useradd --create-home -s /bin/bash user && \
    echo "user:user" | chpasswd && adduser user sudo

USER user

# Add ssh keys for user, as user
ADD --chown=user:user id_rsa.pub /home/user/.ssh/
ADD --chown=user:user id_rsa /home/user/.ssh/
RUN chmod 600 /home/user/.ssh/id_rsa

# Create directory for downloaded files
RUN mkdir /home/user/files

# Copy over app config
ADD --chown=user:user settings.cfg /home/user/.seedsync/

USER root


# Let user run sudo without password
RUN echo "user ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers

WORKDIR /scripts

ADD install_seedsync.sh /scripts/
ADD expect_seedsync.exp /scripts/
ADD entrypoint.sh /scripts/

ENTRYPOINT ["/scripts/entrypoint.sh"]
CMD ["/sbin/init --log-target=journal 3>&1"]

EXPOSE 8800
