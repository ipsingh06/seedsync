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

4. Install the rest:
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

1. Run these commands inside the root directory
```bash
make clean
make
```

2. The .deb package will be generated inside `build` directory.
   The docker image will be listed under `docker image ls`

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
   | Parameters  | -c build/config --html ../angular/dist --scanfs build/scanfs |

   

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
./scripts/tests/run_angular_tests.py
./scripts/tests/run_python_tests.py
./scripts/tests/run_e2e_tests.py -d <path to deb file> -i <image version>
```

# Release

## Checklist

1. Do all of these in one change
    1. Version update in `src/angular/package.json`
    3. Version update and changelog in `src/debian/changelog`.
       Use command `LANG=C date -R` to get the date.
    4. Update `src/e2e/tests/about.page.spec.ts`
2. Tag the commit as vX.X.X
3. make clean && make
4. Run all 3 tests
5. Upload deb file to github
6. Tag and upload image to Dockerhub (see below)

## Docker image upload to Dockerhub

```bash
USERNAME="ipsingh06"
IMAGE="seedsync"
VERSION="<version number here>"
docker tag ${IMAGE}:latest ${USERNAME}/${IMAGE}:latest
docker tag ${IMAGE}:latest ${USERNAME}/${IMAGE}:${VERSION}
docker push ${USERNAME}/${IMAGE}:latest
docker push ${USERNAME}/${IMAGE}:${VERSION}
```

