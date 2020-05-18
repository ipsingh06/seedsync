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

	# angular html image
	DOCKER_BUILDKIT=1 docker build \
		-f ${SOURCEDIR}/docker/build/deb/Dockerfile \
		--target seedsync_build_html_export \
		--tag seedsync/build/html/export \
		${ROOTDIR}

	# final image
	DOCKER_BUILDKIT=1 docker build \
		-f ${SOURCEDIR}/docker/build/docker-image/Dockerfile \
		--target seedsync_run \
		--tag seedsync:latest \
		${ROOTDIR}

clean:
	rm -rf ${BUILDDIR}
