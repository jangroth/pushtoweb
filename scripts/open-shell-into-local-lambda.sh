#!/bin/bash -eux

CONTAINER_NAME='lambda_local'

if [[ -n `docker ps --quiet --filter "name=$CONTAINER_NAME"` ]] ; then
  docker rm --force $CONTAINER_NAME
fi

CONTAINER_ID=`docker run \
    --volume $PWD/../lambda:/var/task \
    --name $CONTAINER_NAME \
    --detach \
    lambci/lambda:python3.6 cloneintobucket.handler '{"local": "true"}'`

docker exec --interactive --tty $CONTAINER_ID /bin/bash
