#!/usr/bin/env bash
set -e
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

ARTIFACTS_VERSION=`cat ${DIR}/ARTIFACTS_VERSION`

IMAGE="seedsync"
VERSION=`cat ${DIR}/VERSION`

if [ "${ARTIFACTS_VERSION}" != "${VERSION}" ]; then
    echo "ERROR: Image version (${VERSION}) mismatches artifacts version (${ARTIFACTS_VERSION})"
    exit 1
fi

docker build -t ${IMAGE}:${VERSION} ${DIR}/

echo "Finished building docker image ${IMAGE}:${VERSION}"
