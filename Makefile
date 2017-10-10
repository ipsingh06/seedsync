# Copyright 2017, Inderpreet Singh, All rights reserved.

SOURCEDIR:=$(shell realpath ./src)
BUILDDIR:=$(shell realpath ./build)

.PHONY: py ng builddir clean

all: py ng artifacts

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

clean:
	rm -rf build