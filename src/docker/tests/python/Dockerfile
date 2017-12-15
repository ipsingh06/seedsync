FROM ubuntu:16.04

# install OS dependencies
RUN apt-get update && apt-get install -y \
    openssh-server \
    lftp \
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

EXPOSE 22

# src needs to be mounted on /src/
WORKDIR /src/

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["green", "-vv"]
