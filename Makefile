# Copyright 2017, Inderpreet Singh, All rights reserved.

SOURCEDIR:=$(shell realpath ./src)
BUILDDIR:=$(shell realpath ./build)

.PHONY: py scanfs ng artifacts deb builddir clean

all: py scanfs ng artifacts deb docker

builddir:
	mkdir -p build

py: builddir
	pyinstaller ${SOURCEDIR}/python/seedsync.py \
		-y \
		-p ${SOURCEDIR}/python \
		--distpath ${BUILDDIR}/py-dist \
		--workpath ${BUILDDIR}/py-work \
		--specpath ${BUILDDIR} \
		--additional-hooks-dir ${SOURCEDIR}/pyinstaller_hooks/ \
		--name seedsync

scanfs: builddir
	pyinstaller ${SOURCEDIR}/python/scan_fs.py \
		-y \
		--onefile \
		-p ${SOURCEDIR}/python \
		--distpath ${BUILDDIR}/scanfs-dist \
		--workpath ${BUILDDIR}/scanfs-work \
		--specpath ${BUILDDIR} \
		--name scanfs

ng: builddir
	cd ${SOURCEDIR}/angular && \
	ng build -prod --output-path ${BUILDDIR}/ng-dist

artifacts:
	rm -rf ${BUILDDIR}/artifacts
	mkdir -p ${BUILDDIR}/artifacts
	cp -rf ${BUILDDIR}/py-dist/seedsync/* ${BUILDDIR}/artifacts/
	cp -rf ${BUILDDIR}/ng-dist ${BUILDDIR}/artifacts/html
	cp -f ${BUILDDIR}/scanfs-dist/scanfs ${BUILDDIR}/artifacts/
	cat ${SOURCEDIR}/debian/changelog \
        | grep -m1 -o "seedsync \(([0-9\.\-]*)\) stable" \
        | grep -o [0-9\.\-]* \
        | sed 's/\-/\./' \
        > ${BUILDDIR}/artifacts/VERSION

deb:
	rm -rf ${BUILDDIR}/deb
	mkdir -p ${BUILDDIR}/deb
	cp -rf ${BUILDDIR}/artifacts ${BUILDDIR}/deb/seedsync
	cp -rf ${SOURCEDIR}/debian ${BUILDDIR}/deb/
	cd ${BUILDDIR}/deb && dpkg-buildpackage -B -uc -us

docker:
	rm -rf ${BUILDDIR}/docker
	mkdir -p ${BUILDDIR}/docker
	cp -rf ${SOURCEDIR}/python ${BUILDDIR}/docker/python
	cp -rf ${BUILDDIR}/artifacts/html ${BUILDDIR}/docker/html
	cp -rf ${BUILDDIR}/artifacts/scanfs ${BUILDDIR}/docker/scanfs
	cp -rf ${BUILDDIR}/artifacts/VERSION ${BUILDDIR}/docker/ARTIFACTS_VERSION
	cp -rf ${SOURCEDIR}/docker/release/. ${BUILDDIR}/docker/
	${BUILDDIR}/docker/build.sh

clean:
	rm -rf build