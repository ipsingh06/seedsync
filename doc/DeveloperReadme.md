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

# Build

1. Run these commands inside the root directory
```bash
make clean
make
```

2. The .deb package will be generated inside build/ directory.


# Run tests
```bash
./scripts/tests/run_angular_tests.sh
./scripts/tests/run_python_tests.sh
./scripts/tests/run_e2e_tests.sh -f <path to deb file>
```
