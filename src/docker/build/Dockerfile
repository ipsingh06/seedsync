# Creates environment to build python binaries
FROM ubuntu:16.04 as python_build
RUN apt-get update && apt-get install -y software-properties-common
RUN add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && apt-get install -y \
    python3.7 \
    python3.7-dev \
    python3.7-distutils \
    python3-pip
# Switch to Python 3.7
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.7 1
RUN update-alternatives --set python /usr/bin/python3.7
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.7 1
RUN update-alternatives --set python3 /usr/bin/python3.7
RUN pip3 install pipenv
COPY src/python/Pipfile /python/
COPY src/python/Pipfile.lock /python/
WORKDIR /python
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8
RUN pipenv install --system --deploy


# Builds seedsync with pyinstaller
# Output is in /build/dist/seedsync/
FROM python_build as pyinstaller_seedsync
COPY src/python /python
COPY src/pyinstaller_hooks /pyinstaller_hooks
RUN mkdir -p /build
RUN pyinstaller /python/seedsync.py \
    -y \
    -p /python \
    --distpath /build/dist \
    --workpath /build/work \
    --specpath /build \
    --additional-hooks-dir /pyinstaller_hooks/ \
    --hidden-import="pkg_resources.py2_warn" \
    --name seedsync


# Builds scanfs with pyinstaller
# Output is in /build/dist/
FROM python_build as pyinstaller_scanfs
COPY src/python /python
RUN mkdir -p /build
RUN	pyinstaller /python/scan_fs.py \
    -y \
    --onefile \
    -p /python \
    --distpath /build/dist \
    --workpath /build/work \
    --specpath /build \
    --name scanfs


# Builds angular app
# Output is in /build/dist/
FROM node:12.16 as node_angular
COPY src/angular /angular
WORKDIR /angular
RUN npm install
RUN node_modules/@angular/cli/bin/ng build -prod --output-path /build/dist/


# Creates environment to build deb packages
FROM ubuntu:16.04 as deb_build
RUN apt-get update
RUN apt-get install -y build-essential dh-systemd debhelper
RUN apt-get install -y devscripts


# Builds debian package
# Output is in /build/dist/
FROM deb_build as seedsync_deb
RUN mkdir -p /build/work
COPY src/debian /build/work/debian
COPY --from=pyinstaller_seedsync /build/dist/seedsync /build/work/seedsync
COPY --from=pyinstaller_scanfs /build/dist/scanfs /build/work/seedsync/
COPY --from=node_angular /build/dist /build/work/seedsync/html
WORKDIR /build/work
RUN dpkg-buildpackage -B -uc -us
RUN ls /build/*.deb && echo "----" && ls /build/work


# Exports deb package to host
FROM scratch AS export_deb
COPY --from=seedsync_deb /build/*.deb .

# Exports scanfs to host
FROM scratch AS export_scanfs
COPY --from=pyinstaller_scanfs /build/dist/scanfs .
