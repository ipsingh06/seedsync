FROM ubuntu:18.04

# install OS dependencies
RUN apt-get update && apt-get install -y \
    openssh-server \
    lftp \
    rar \
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

# install python dependencies
ADD Pipfile /app/
ADD Pipfile.lock /app/
RUN cd /app/ && LC_ALL=C.UTF-8 LANG=C.UTF-8 pipenv install --system --deploy

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
