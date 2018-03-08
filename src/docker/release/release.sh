#!/usr/bin/env bash
set -e
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

USERNAME="ipsingh06"
IMAGE="seedsync"
VERSION=`cat ${DIR}/VERSION`

docker tag ${IMAGE}:${VERSION} ${USERNAME}/${IMAGE}:latest
docker tag ${IMAGE}:${VERSION} ${USERNAME}/${IMAGE}:${VERSION}

docker push ${USERNAME}/${IMAGE}:latest
docker push ${USERNAME}/${IMAGE}:${VERSION}

echo "Pushed docker image ${USERNAME}/${IMAGE}:${VERSION}"
