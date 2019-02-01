# Environment Setup

## Install dependencies
1. Install angular and its dependencies:
https://angular.io/guide/quickstart

2. Install pip:
https://pip.pypa.io/en/stable/installing/

3. Install docker and docker-compose:
https://docs.docker.com/engine/installation/linux/docker-ce/ubuntu/#install-docker-ce
https://docs.docker.com/compose/install/

4. Install the rest:
```bash
sudo apt-get install -y \
    python3-dev \
    debhelper \
    dh-systemd \
    rar
sudo pip install virtualenvwrapper
```

## Fetch code
```bash
git clone git@gitlab.com:ipsingh06/seedsync.git
cd seedsync
```

## Setup python virtual environment
```bash
mkvirtualenv -p python3.5 seedsync
pip install -r src/python/requirements.txt
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

2. The .deb package will be generated inside build/ directory.
   The docker image will be listed under `docker image ls`.


# Setup dev environment

## PyCharm
1. Switch interpreter to virtualenv
2. Mark src/python as 'Sources Root'


# Run tests
## Prerequisites
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

## Python Unit Tests
Run from PyCharm

## Angular Unit Tests
```bash
cd src/angular
ng test
```

## Docker-based Test Suite
```bash
./scripts/tests/run_angular_tests.py
./scripts/tests/run_python_tests.py
./scripts/tests/run_e2e_tests.py -d <path to deb file> -i <image version>
```

# Release Checklist

1. Do all of these in one change
    1. Version update in src/angular/package.json
    2. Version update in src/docker/release/VERSION
    3. Version update and changelog in src/debian/changelog.
       Use command `LANG=C date -R` to get the date.
    4. Update src/e2e/tests/about.page.spec.ts
2. Tag the commit as vX.X-X
3. make clean && make
4. Run all 3 tests
5. Upload deb file to github
6. Run release.sh in build/docker
