# Copyright 2017, Inderpreet Singh, All rights reserved.

ROOTDIR:=$(shell realpath .)
SOURCEDIR:=$(shell realpath ./src)
BUILDDIR:=$(shell realpath ./build)

.PHONY: deb builddir docker clean

all: deb docker

builddir:
	mkdir -p ${BUILDDIR}

scanfs: builddir
	DOCKER_BUILDKIT=1 docker build \
		-f ${SOURCEDIR}/docker/build/Dockerfile \
		--target export_scanfs \
		--output ${BUILDDIR} \
		${ROOTDIR}

deb: builddir
	DOCKER_BUILDKIT=1 docker build \
		-f ${SOURCEDIR}/docker/build/Dockerfile \
		--target export_deb \
		--output ${BUILDDIR} \
		${ROOTDIR}

docker: builddir
	rm -rf ${BUILDDIR}/docker
	mkdir -p ${BUILDDIR}/docker
	cp -rf ${SOURCEDIR}/python ${BUILDDIR}/docker/python
	cp -rf ${BUILDDIR}/artifacts/html ${BUILDDIR}/docker/html
	cp -rf ${BUILDDIR}/artifacts/scanfs ${BUILDDIR}/docker/scanfs
	cp -rf ${BUILDDIR}/artifacts/VERSION ${BUILDDIR}/docker/ARTIFACTS_VERSION
	cp -rf ${SOURCEDIR}/docker/release/. ${BUILDDIR}/docker/
	${BUILDDIR}/docker/build.sh

clean:
	rm -rf ${BUILDDIR}
