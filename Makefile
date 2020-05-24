# Copyright 2017, Inderpreet Singh, All rights reserved.

# Catch sigterms
# See: https://stackoverflow.com/a/52159940
export SHELL:=/bin/bash
export SHELLOPTS:=$(if $(SHELLOPTS),$(SHELLOPTS):)pipefail:errexit
.ONESHELL:

ROOTDIR:=$(shell realpath .)
SOURCEDIR:=$(shell realpath ./src)
BUILDDIR:=$(shell realpath ./build)

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

docker-image:
	# scanfs image
	$(DOCKER) build \
		-f ${SOURCEDIR}/docker/build/deb/Dockerfile \
		--target seedsync_build_scanfs_export \
		--tag seedsync/build/scanfs/export \
		${ROOTDIR}

	# angular html export
	$(DOCKER) build \
		-f ${SOURCEDIR}/docker/build/deb/Dockerfile \
		--target seedsync_build_angular_export \
		--tag seedsync/build/angular/export \
		${ROOTDIR}

	# final image
	$(DOCKER) build \
		-f ${SOURCEDIR}/docker/build/docker-image/Dockerfile \
		--target seedsync_run \
		--tag seedsync:latest \
		${ROOTDIR}

tests-python:
	# python run
	$(DOCKER) build \
		-f ${SOURCEDIR}/docker/build/docker-image/Dockerfile \
		--target seedsync_run_python_env \
		--tag seedsync/run/python/env \
		${ROOTDIR}
	# python tests
	$(DOCKER_COMPOSE) \
		-f ${SOURCEDIR}/docker/test/python/compose.yml \
		build

run-tests-python: tests-python
	$(DOCKER_COMPOSE) \
		-f ${SOURCEDIR}/docker/test/python/compose.yml \
		up --force-recreate

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
		up --force-recreate


# TODO: add debian install compose
# TODO: make tests image wait for config to be updated before running
tests-e2e:
	# e2e tests
	if [[ "${DEV}" = "1" ]] ; then
		COMPOSE_FLAGS="-f ${SOURCEDIR}/docker/test/e2e/compose-dev.yml"
	fi

	$(DOCKER_COMPOSE) \
		-f ${SOURCEDIR}/docker/test/e2e/compose.yml \
		-f ${SOURCEDIR}/docker/stage/docker-image/compose.yml \
		$${COMPOSE_FLAGS} \
		build


run-tests-e2e: tests-e2e
	if [[ -z "${SEEDSYNC_VERSION}" ]] ; then \
		echo "ERROR: One of SEEDSYNC_VERSION or DEB_PATH must be set"; exit 1; \
  	fi

	if [[ "${DEV}" = "1" ]] ; then
		COMPOSE_FLAGS="-f ${SOURCEDIR}/docker/test/e2e/compose-dev.yml"
	else \
  		COMPOSE_RUN_FLAGS="-d"
	fi

	function tearDown {
		$(DOCKER_COMPOSE) \
			-f ${SOURCEDIR}/docker/test/e2e/compose.yml \
			-f ${SOURCEDIR}/docker/stage/docker-image/compose.yml \
			$${COMPOSE_FLAGS} \
			stop
	}
	trap tearDown EXIT


	if [[ ! -z "${SEEDSYNC_VERSION}" ]] ; then \
		$(DOCKER_COMPOSE) \
			-f ${SOURCEDIR}/docker/test/e2e/compose.yml \
			-f ${SOURCEDIR}/docker/stage/docker-image/compose.yml \
			$${COMPOSE_FLAGS} \
			up --force-recreate \
			$${COMPOSE_RUN_FLAGS}

		if [[ "${DEV}" != "1" ]] ; then
			$(DOCKER) logs -f seedsync_test_e2e
		fi
	fi

clean:
	rm -rf ${BUILDDIR}
