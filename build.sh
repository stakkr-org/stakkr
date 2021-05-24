#!/bin/bash

set -e

if [[ -z "$1" ]]; then
    echo "You must define a valid version to build as parameter (exemple: 4.0rc1)"
    exit 1
fi

VERSION=$1
GREEN='\033[0;32m'
NC='\033[0m' # No Color
TAG=stakkr/stakkr:${VERSION}


# Build Image
echo "Building ${TAG}"
docker build --tag ${TAG} \
             --progress=plain \
             --cache-from ${TAG} \
             --build-arg STAKKR_VERSION="${VERSION}" \
             --build-arg BUILD_DATE="$(date -u +'%Y-%m-%dT%H:%M:%SZ')" \
             --build-arg VCS_REF="$(git rev-parse --short HEAD)" \
             --build-arg DOCKER_TAG="${TAG}" \
             .
echo "${TAG} will also be tagged 'latest'"
docker tag ${TAG} stakkr/stakkr:latest

echo ""
if [[ $? -eq 0 ]]; then
    echo -e "${GREEN}Build Done${NC}."
    echo ""
    echo "To push that version (and other of the same repo):"
    echo "  docker push stakkr/stakkr"
fi
