# Copyright 2017, Inderpreet Singh, All rights reserved.

SOURCEDIR:=$(shell realpath ./src)
BUILDDIR:=$(shell realpath ./build)

.PHONY: py ng artifacts deb builddir clean

all: py ng artifacts deb

builddir:
	mkdir -p build

py: builddir
	pyinstaller ${SOURCEDIR}/python/pylftpd.py \
		-y \
		-p ${SOURCEDIR}/python \
		--distpath ${BUILDDIR}/py-dist \
		--workpath ${BUILDDIR}/py-work \
		--specpath ${BUILDDIR}

ng: builddir
	cd ${SOURCEDIR}/angular && \
	ng build -prod --output-path ${BUILDDIR}/ng-dist

artifacts:
	rm -rf ${BUILDDIR}/artifacts
	mkdir -p ${BUILDDIR}/artifacts
	cp -rf ${BUILDDIR}/py-dist/pylftpd/* ${BUILDDIR}/artifacts/
	cp -rf ${BUILDDIR}/ng-dist ${BUILDDIR}/artifacts/html

deb:
	rm -rf ${BUILDDIR}/deb
	mkdir -p ${BUILDDIR}/deb
	cp -rf ${BUILDDIR}/artifacts ${BUILDDIR}/deb/pylftp
	cp -rf ${SOURCEDIR}/debian ${BUILDDIR}/deb/
	cd ${BUILDDIR}/deb && dpkg-buildpackage -B -uc -us

clean:
	rm -rf build