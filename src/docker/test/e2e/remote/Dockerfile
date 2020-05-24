FROM ubuntu:18.04

# Install dependencies
RUN apt-get update && apt-get install -y \
    python3.7

# Switch to Python 3.7
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.7 1
RUN update-alternatives --set python /usr/bin/python3.7

# Create non-root user
RUN useradd --create-home -s /bin/bash remoteuser && \
    echo "remoteuser:remotepass" | chpasswd


# Add install image's user's key to authorized
USER remoteuser
ADD --chown=remoteuser:remoteuser src/docker/test/e2e/remote/id_rsa.pub /home/remoteuser/user_id_rsa.pub
RUN  mkdir -p /home/remoteuser/.ssh && \
    cat /home/remoteuser/user_id_rsa.pub >> /home/remoteuser/.ssh/authorized_keys
USER root

# Copy over data
ADD --chown=remoteuser:remoteuser src/docker/test/e2e/remote/files /home/remoteuser/files

# Install and run ssh server
RUN apt-get update && apt-get install -y openssh-server

# Change port
RUN sed -i '/Port 22/c\Port 1234' /etc/ssh/sshd_config
EXPOSE 1234

RUN mkdir /var/run/sshd

CMD ["/usr/sbin/sshd", "-D"]
