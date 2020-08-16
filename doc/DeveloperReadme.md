# Environment Setup

## Install dependencies
1. Install [nodejs](https://joshtronic.com/2019/04/29/how-to-install-node-v12-on-debian-and-ubuntu/) (comes with npm)

2. Install pipenv:

   ```bash
   sudo apt install -y python3-pip pipenv
   ```

3. Install docker and docker-compose:
https://docs.docker.com/engine/installation/linux/docker-ce/ubuntu/#install-docker-ce
https://docs.docker.com/compose/install/

4. Install docker buildx
   
    1. https://github.com/docker/buildx/issues/132#issuecomment-582218096
    2. https://github.com/docker/buildx/issues/132#issuecomment-636041307
    
5. Build dependencies

   ```bash
   sudo apt-get install -y jq
   ```

6. Install the rest:
   ```bash
   sudo apt-get install -y lftp python3-dev rar
   ```

## Fetch code
```bash
git clone git@gitlab.com:ipsingh06/seedsync.git
cd seedsync
```

## Setup python virtual environment
```bash
cd src/python
PIPENV_VENV_IN_PROJECT=True pipenv install
```

## Setup angular node modules
```bash
cd src/angular
npm install
```

## Setup end-to-end tests node modules
```bash
cd src/e2e
npm install
```

# Build

1. Set up docker buildx for multi-arch builds

   ```bash
   docker buildx create --name mybuilder --driver docker-container --driver-opt image=moby/buildkit:master,network=host
   docker run --rm --privileged multiarch/qemu-user-static --reset -p yes
   docker buildx inspect --bootstrap
   # Make sure the following architectures are listed: linux/amd64, linux/arm64, linux/arm/v7 
   ```

2. Create local docker registry to store multi-arch images

   ```bash
   docker run -d -p 5000:5000 --restart=always --name registry registry:2
   ```

3. Run these commands inside the root directory
   ```bash
   make clean
   make
   ```

4. The .deb package will be generated inside `build` directory.
   The docker image will be pushed to the local registry as `seedsync:latest`. See if using:

   ```bash
   curl -X GET http://localhost:5000/v2/_catalog
   ```



## Python Dev Build and Run

### Build scanfs

```bash
make scanfs
```

### Run python

```bash
cd src/python
mkdir -p build/config
pipenv run python seedsync.py -c build/config --html ../angular/dist --scanfs build/scanfs
```



## Angular Dev Build and Run

```bash
cd src/angular
node_modules/@angular/cli/bin/ng build
node_modules/@angular/cli/bin/ng serve
```

Dev build will be served at [http://localhost:4200](http://localhost:4200)



## Documentation

### Preview documentation in brower

```bash
cd src/python
pipenv run mkdocs serve
```

Preview will be served at  [http://localhost:8000](http://localhost:8000)

### Deploy documentation

```bash
pipenv run mkdocs gh-deploy
git push github gh-pages
```



# Setup dev environment

## PyCharm
1. Set project root to top-level `seedsync` directory

2. Switch interpreter to virtualenv

3. Mark src/python as 'Sources Root'

4. Add run configuration

   | Config      | Value                                                        |
   | ----------- | ------------------------------------------------------------ |
   | Name        | seedsync                                                     |
   | Script path | seedsync.py                                                  |
   | Parameters  | -c ./build/config --html ../angular/dist --scanfs ./build/scanfs |

   

# Run tests

## Manual

### Python Unit Tests

Create a new user account for python tests, and add the current user to its authorized keys.
Also add the test account to the current user group so it may access any files created by the current user.
Note: the current user must have SSH keys already generated.

```bash
sudo adduser -q --disabled-password --disabled-login --gecos 'seedsynctest' seedsynctest
sudo bash -c "echo seedsynctest:seedsyncpass | chpasswd"
sudo -u seedsynctest mkdir /home/seedsynctest/.ssh
sudo -u seedsynctest chmod 700 /home/seedsynctest/.ssh
cat ~/.ssh/id_rsa.pub | sudo -u seedsynctest tee /home/seedsynctest/.ssh/authorized_keys
sudo -u seedsynctest chmod 664 /home/seedsynctest/.ssh/authorized_keys
sudo usermod -a -G $USER seedsynctest
```

Run from PyCharm

OR

Run from ```green```

```bash
cd src/python
pipenv run green -vv
```

### Angular Unit Tests

```bash
cd src/angular
node_modules/@angular/cli/bin/ng test
```

### E2E Tests

[See here](../src/e2e/README.md)

## Docker-based Test Suite

```bash
# Python tests
make run-tests-python

# Angular tests
make run-tests-angular

# E2E Tests
# Docker image (arch=amd64,arm64,arm/v7)
make run-tests-e2e SEEDSYNC_VERSION=latest SEEDSYNC_ARCH=<arch code>
# Debian package (os=ubu1604,ubu1804,ubu2004)
make run-tests-e2e SEEDSYNC_DEB=`readlink -f build/*.deb` SEEDSYNC_OS=<os code>
```

To test image from a registry other than the local, use `SEEDSYNC_REGISTRY=`.
For example:

```bash
make run-tests-e2e SEEDSYNC_VERSION=latest SEEDSYNC_ARCH=arm64 SEEDSYNC_REGISTRY=ipsingh06
```



# Release

## Checklist

1. Do all of these in one change
    1. Version update in `src/angular/package.json`
    2. Version update and changelog in `src/debian/changelog`.
       Use command `LANG=C date -R` to get the date.
    3. Update `src/e2e/tests/about.page.spec.ts`
    4. Update Copyright date in `about-page.component.html`
2. Tag the commit as vX.X.X
3. make clean && make
4. Run all tests
5. Upload deb file to github
6. Tag and upload image to Dockerhub (see below)

## Docker image upload to Dockerhub

```bash
make docker-image-release VERSION=<version> REPO=ipsingh06
make docker-image-release VERSION=latest REPO=ipsingh06
```



# Development

## Remote Server

Use the following command to run the docker image for the remote server for development testing.
This is the same image used by the end-to-end tests.

```bash
make run-remote-server
```

The connection parameters for the remote server are:

| Option         | Value                             |
| -------------- | --------------------------------- |
| Remote Address | localhost or host.docker.internal |
| Remote Port    | 1234                              |
| Username       | remoteuser                        |
| Pass           | remotepass                        |
| Remote Path    | /home/remoteuser/files            |

