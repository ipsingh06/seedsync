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

# Copy over data
ADD --chown=remoteuser:remoteuser ./files /home/remoteuser/files

# Install and run ssh server
RUN apt-get update && apt-get install -y openssh-server

# Change port
RUN sed -i '/Port 22/c\Port 1234' /etc/ssh/sshd_config
EXPOSE 1234

RUN mkdir /var/run/sshd

CMD ["/usr/sbin/sshd", "-D"]