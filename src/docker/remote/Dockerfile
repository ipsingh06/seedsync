FROM ubuntu:14.04

# Create non-root user
RUN useradd --create-home -s /bin/bash remoteuser && \
    echo "remoteuser:remotepass" | chpasswd


# Add install image's user's key to authorized
USER remoteuser
ADD --chown=remoteuser:remoteuser id_rsa.pub /home/remoteuser/user_id_rsa.pub
RUN  mkdir -p /home/remoteuser/.ssh && \
    cat /home/remoteuser/user_id_rsa.pub >> /home/remoteuser/.ssh/authorized_keys
USER root

# Install and run ssh server
RUN apt-get update && apt-get install -y openssh-server

RUN mkdir /var/run/sshd

EXPOSE 22
CMD ["/usr/sbin/sshd", "-D"]