# Copyright 2017, Inderpreet Singh, All rights reserved.

# Catch sigterms
# See: https://stackoverflow.com/a/52159940
export SHELL:=/bin/bash
export SHELLOPTS:=$(if $(SHELLOPTS),$(SHELLOPTS):)pipefail:errexit
.ONESHELL:

# Color outputs
red=`tput setaf 1`
green=`tput setaf 2`
reset=`tput sgr0`

ROOTDIR:=$(shell realpath .)
SOURCEDIR:=$(shell realpath ./src)
BUILDDIR:=$(shell realpath ./build)
DEFAULT_REGISTRY:=localhost:5000

#DOCKER_BUILDKIT_FLAGS=BUILDKIT_PROGRESS=plain
DOCKER=${DOCKER_BUILDKIT_FLAGS} DOCKER_BUILDKIT=1 docker
DOCKER_COMPOSE=${DOCKER_BUILDKIT_FLAGS} COMPOSE_DOCKER_CLI_BUILD=1 DOCKER_BUILDKIT=1 docker-compose

.PHONY: builddir deb docker-image clean

all: deb docker-image

builddir:
	mkdir -p ${BUILDDIR}

scanfs: builddir
	$(DOCKER) build \
		-f ${SOURCEDIR}/docker/build/deb/Dockerfile \
		--target seedsync_build_scanfs_export \
		--output ${BUILDDIR} \
		${ROOTDIR}

deb: builddir
	$(DOCKER) build \
		-f ${SOURCEDIR}/docker/build/deb/Dockerfile \
		--target seedsync_build_deb_export \
		--output ${BUILDDIR} \
		${ROOTDIR}

docker-buildx:
	$(DOCKER) run --rm --privileged multiarch/qemu-user-static --reset -p yes

docker-image: docker-buildx
	# scanfs image
	$(DOCKER) buildx build \
		-f ${SOURCEDIR}/docker/build/deb/Dockerfile \
		--target seedsync_build_scanfs_export \
		--tag ${DEFAULT_REGISTRY}/seedsync/build/scanfs/export \
		--push \
		${ROOTDIR}

	# angular html export
	$(DOCKER) buildx build \
		-f ${SOURCEDIR}/docker/build/deb/Dockerfile \
		--target seedsync_build_angular_export \
		--tag ${DEFAULT_REGISTRY}/seedsync/build/angular/export \
		--push \
		${ROOTDIR}

	# final image
	$(DOCKER) buildx build \
		-f ${SOURCEDIR}/docker/build/docker-image/Dockerfile \
		--target seedsync_run \
		--build-arg REGISTRY=${DEFAULT_REGISTRY} \
		--tag ${DEFAULT_REGISTRY}/seedsync:latest \
		--platform linux/amd64,linux/arm64,linux/arm/v7 \
		--push \
		${ROOTDIR}

docker-image-release:
	@if [[ -z "${VERSION}" ]] ; then \
		echo "${red}ERROR: VERSION is required${reset}"; exit 1; \
	fi
	@if [[ -z "${REPO}" ]] ; then \
		echo "${red}ERROR: REPO is required${reset}"; exit 1; \
	fi
	echo "${green}VERSION=${VERSION}${reset}"
	echo "${green}REPO=${REPO}${reset}"

	# final image
	$(DOCKER) buildx build \
		-f ${SOURCEDIR}/docker/build/docker-image/Dockerfile \
		--target seedsync_run \
		--build-arg REGISTRY=${DEFAULT_REGISTRY} \
		--tag ${REPO}/seedsync:${VERSION} \
		--platform linux/amd64,linux/arm64,linux/arm/v7 \
		--push \
		${ROOTDIR}

tests-python:
	# python run
	$(DOCKER) build \
		-f ${SOURCEDIR}/docker/build/docker-image/Dockerfile \
		--target seedsync_run_python_devenv \
		--tag seedsync/run/python/devenv \
		${ROOTDIR}
	# python tests
	$(DOCKER_COMPOSE) \
		-f ${SOURCEDIR}/docker/test/python/compose.yml \
		build

run-tests-python: tests-python
	$(DOCKER_COMPOSE) \
		-f ${SOURCEDIR}/docker/test/python/compose.yml \
		up --force-recreate --exit-code-from tests

tests-angular:
	# angular build
	$(DOCKER) build \
		-f ${SOURCEDIR}/docker/build/deb/Dockerfile \
		--target seedsync_build_angular_env \
		--tag seedsync/build/angular/env \
		${ROOTDIR}
	# angular tests
	$(DOCKER_COMPOSE) \
		-f ${SOURCEDIR}/docker/test/angular/compose.yml \
		build

run-tests-angular: tests-angular
	$(DOCKER_COMPOSE) \
		-f ${SOURCEDIR}/docker/test/angular/compose.yml \
		up --force-recreate --exit-code-from tests

tests-e2e-deps:
	# deb pre-reqs
	$(DOCKER) build \
		${SOURCEDIR}/docker/stage/deb/ubuntu-systemd/ubuntu-16.04-systemd \
		-t ubuntu-systemd:16.04
	$(DOCKER) build \
		${SOURCEDIR}/docker/stage/deb/ubuntu-systemd/ubuntu-18.04-systemd \
		-t ubuntu-systemd:18.04
	$(DOCKER) build \
		${SOURCEDIR}/docker/stage/deb/ubuntu-systemd/ubuntu-20.04-systemd \
		-t ubuntu-systemd:20.04

	# Setup docker for the systemd container
	# See: https://github.com/solita/docker-systemd
	$(DOCKER) run --rm --privileged -v /:/host solita/ubuntu-systemd setup

run-tests-e2e: tests-e2e-deps
	# Check our settings
	@if [[ -z "${SEEDSYNC_VERSION}" ]] && [[ -z "${SEEDSYNC_DEB}" ]]; then \
		echo "${red}ERROR: One of SEEDSYNC_VERSION or SEEDSYNC_DEB must be set${reset}"; exit 1; \
	elif [[ ! -z "${SEEDSYNC_VERSION}" ]] && [[ ! -z "${SEEDSYNC_DEB}" ]]; then \
	  	echo "${red}ERROR: Only one of SEEDSYNC_VERSION or SEEDSYNC_DEB must be set${reset}"; exit 1; \
  	fi

	# Set up environment for deb
	@if [[ ! -z "${SEEDSYNC_DEB}" ]] ; then \
		if [[ -z "${SEEDSYNC_OS}" ]] ; then \
			echo "${red}ERROR: SEEDSYNC_OS is required for DEB e2e test${reset}"; \
			echo "${red}Options include: ubu1604, ubu1804, ubu2004${reset}"; exit 1; \
		fi
	fi

	# Set up environment for image
	@if [[ ! -z "${SEEDSYNC_VERSION}" ]] ; then \
		if [[ -z "${SEEDSYNC_ARCH}" ]] ; then \
			echo "${red}ERROR: SEEDSYNC_ARCH is required for docker image e2e test${reset}"; \
			echo "${red}Options include: amd64, arm64, arm/v7${reset}"; exit 1; \
		fi
		if [[ -z "${SEEDSYNC_REGISTRY}" ]] ; then \
			export SEEDSYNC_REGISTRY="${DEFAULT_REGISTRY}"; \
		fi;
		echo "${green}REGISTRY=$${SEEDSYNC_REGISTRY}${reset}";
		# Removing and pulling is the only way to select the arch from a multi-arch image :(
		$(DOCKER) rmi -f $${SEEDSYNC_REGISTRY}/seedsync:$${SEEDSYNC_VERSION}
		$(DOCKER) pull $${SEEDSYNC_REGISTRY}/seedsync:$${SEEDSYNC_VERSION} --platform linux/$${SEEDSYNC_ARCH}
	fi

	# Set the flags
	COMPOSE_FLAGS="-f ${SOURCEDIR}/docker/test/e2e/compose.yml "
	COMPOSE_RUN_FLAGS=""
	if [[ ! -z "${SEEDSYNC_DEB}" ]] ; then
		COMPOSE_FLAGS+="-f ${SOURCEDIR}/docker/stage/deb/compose.yml "
		COMPOSE_FLAGS+="-f ${SOURCEDIR}/docker/stage/deb/compose-${SEEDSYNC_OS}.yml "
	fi
	if [[ ! -z "${SEEDSYNC_VERSION}" ]] ; then \
		COMPOSE_FLAGS+="-f ${SOURCEDIR}/docker/stage/docker-image/compose.yml "
	fi
	if [[ "${DEV}" = "1" ]] ; then
		COMPOSE_FLAGS+="-f ${SOURCEDIR}/docker/test/e2e/compose-dev.yml "
	else \
  		COMPOSE_RUN_FLAGS+="-d"
	fi
	echo "${green}COMPOSE_FLAGS=$${COMPOSE_FLAGS}${reset}"

	# Set up Ctrl-C handler
	function tearDown {
		$(DOCKER_COMPOSE) \
			$${COMPOSE_FLAGS} \
			stop
	}
	trap tearDown EXIT

	# Build the test
	echo "${green}Building the tests${reset}"
	$(DOCKER_COMPOSE) \
		$${COMPOSE_FLAGS} \
		build

	# This suppresses the docker-compose error that image has changed
	$(DOCKER_COMPOSE) \
		$${COMPOSE_FLAGS} \
		rm -f myapp

	# Run the test
	echo "${green}Running the tests${reset}"
	$(DOCKER_COMPOSE) \
		$${COMPOSE_FLAGS} \
		up --force-recreate \
		$${COMPOSE_RUN_FLAGS}

	if [[ "${DEV}" != "1" ]] ; then
		$(DOCKER) logs -f seedsync_test_e2e
	fi

	EXITCODE=`$(DOCKER) inspect seedsync_test_e2e | jq '.[].State.ExitCode'`
	if [[ "$${EXITCODE}" != "0" ]] ; then
		false
	fi

run-remote-server:
	$(DOCKER) container rm -f seedsync_test_e2e_remote-dev
	$(DOCKER) run \
		-it --init \
		-p 1234:1234 \
		--name seedsync_test_e2e_remote-dev \
		seedsync/test/e2e/remote

clean:
	rm -rf ${BUILDDIR}
