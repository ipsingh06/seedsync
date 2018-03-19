FROM ubuntu:16.04

# install OS dependencies
RUN apt-get update && apt-get install -y \
    openssh-server \
    lftp \
    rar \
    python3-pip

# install python dependencies
ADD requirements.txt /app/
RUN pip3 install -r /app/requirements.txt

ADD entrypoint.sh /app/

# setup sshd
RUN mkdir /var/run/sshd
RUN ssh-keygen -t rsa -N "" -f /root/.ssh/id_rsa && \
    cat /root/.ssh/id_rsa.pub >> /root/.ssh/authorized_keys
# Disable the known hosts prompt
RUN echo "StrictHostKeyChecking no\nUserKnownHostsFile /dev/null\nLogLevel=quiet" > /root/.ssh/config

# create the seedsynctest user, add root's public key to seedsynctest
RUN useradd --create-home -s /bin/bash seedsynctest && \
    echo "seedsynctest:seedsyncpass" | chpasswd
RUN usermod -a -G root seedsynctest
RUN cp /root/.ssh/id_rsa.pub /home/seedsynctest/ && \
    chown seedsynctest:seedsynctest /home/seedsynctest/id_rsa.pub
USER seedsynctest
RUN  mkdir -p /home/seedsynctest/.ssh && \
    cat /home/seedsynctest/id_rsa.pub >> /home/seedsynctest/.ssh/authorized_keys
USER root

EXPOSE 22

# src needs to be mounted on /src/
WORKDIR /src/

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["green", "-vv"]
