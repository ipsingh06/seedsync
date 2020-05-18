# Copyright 2017, Inderpreet Singh, All rights reserved.

ROOTDIR:=$(shell realpath .)
SOURCEDIR:=$(shell realpath ./src)
BUILDDIR:=$(shell realpath ./build)

.PHONY: builddir deb docker-image clean

all: deb docker-image

builddir:
	mkdir -p ${BUILDDIR}

scanfs: builddir
	DOCKER_BUILDKIT=1 docker build \
		-f ${SOURCEDIR}/docker/build/deb/Dockerfile \
		--target seedsync_build_scanfs_export \
		--output ${BUILDDIR} \
		${ROOTDIR}

deb: builddir
	DOCKER_BUILDKIT=1 docker build \
		-f ${SOURCEDIR}/docker/build/deb/Dockerfile \
		--target seedsync_build_deb_export \
		--output ${BUILDDIR} \
		${ROOTDIR}

docker-image:
	# scanfs image
	DOCKER_BUILDKIT=1 docker build \
		-f ${SOURCEDIR}/docker/build/deb/Dockerfile \
		--target seedsync_build_scanfs_export \
		--tag seedsync/build/scanfs/export \
		${ROOTDIR}

	# angular html export
	DOCKER_BUILDKIT=1 docker build \
		-f ${SOURCEDIR}/docker/build/deb/Dockerfile \
		--target seedsync_build_angular_export \
		--tag seedsync/build/angular/export \
		${ROOTDIR}

	# final image
	DOCKER_BUILDKIT=1 docker build \
		-f ${SOURCEDIR}/docker/build/docker-image/Dockerfile \
		--target seedsync_run \
		--tag seedsync:latest \
		${ROOTDIR}

tests-python:
	# python run
	DOCKER_BUILDKIT=1 docker build \
		-f ${SOURCEDIR}/docker/build/docker-image/Dockerfile \
		--target seedsync_run_python_env \
		--tag seedsync/run/python/env \
		${ROOTDIR}
	# python tests
	COMPOSE_DOCKER_CLI_BUILD=1 DOCKER_BUILDKIT=1 docker-compose \
		-f ${SOURCEDIR}/docker/test/python/compose.yml \
		build

tests-angular:
	# angular build
	DOCKER_BUILDKIT=1 docker build \
		-f ${SOURCEDIR}/docker/build/deb/Dockerfile \
		--target seedsync_build_angular_env \
		--tag seedsync/build/angular/env \
		${ROOTDIR}
	# angular tests
	COMPOSE_DOCKER_CLI_BUILD=1 DOCKER_BUILDKIT=1 docker-compose \
		-f ${SOURCEDIR}/docker/test/angular/compose.yml \
		build

run-tests-python: tests-python
	COMPOSE_DOCKER_CLI_BUILD=1 DOCKER_BUILDKIT=1 docker-compose \
		-f ${SOURCEDIR}/docker/test/python/compose.yml \
		up --force-recreate

run-tests-angular: tests-angular
	COMPOSE_DOCKER_CLI_BUILD=1 DOCKER_BUILDKIT=1 docker-compose \
		-f ${SOURCEDIR}/docker/test/angular/compose.yml \
		up --force-recreate

clean:
	rm -rf ${BUILDDIR}
