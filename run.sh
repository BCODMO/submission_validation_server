#!/bin/bash
set -a && source .env
if [ -z "$PORT" ]; then
    echo "PORT env variable has to be set"
    exit 1
fi
if [ -z "$ENVIRONMENT" ]; then
    echo "ENVIRONMENT env variable has to be set"
    exit 1
fi
CONTAINER_NAME="submission-validation-container-$ENVIRONMENT"
IMAGE_NAME="submission-validation-image-$ENVIRONMENT"
docker rm -f $CONTAINER_NAME
docker rmi `docker images --filter dangling=true -q` 2> /dev/null
docker build --force-rm --no-cache -t $IMAGE_NAME \
    --build-arg GITHUB_OAUTH_TOKEN="$GITHUB_OAUTH_TOKEN" \
    --build-arg PORT="$PORT" \
    . && \
    docker run -d \
    --name $CONTAINER_NAME \
    --env-file=.env \
    -p $PORT:$PORT \
    --rm \
    $IMAGE_NAME

