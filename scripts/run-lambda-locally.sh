#!/bin/bash -eux

CONTAINER_NAME='lambda_local'
cp $PWD/../code/cloneintobucket.py $PWD/../build

if [[ -n `docker ps --quiet --all --filter "name=$CONTAINER_NAME"` ]] ; then
    echo 'Removing existing container...'
    docker rm --force ${CONTAINER_NAME}
fi

CONTAINER_ID=`docker run \
    --volume $PWD/../build:/var/task \
    --name ${CONTAINER_NAME} \
    --detach \
    lambci/lambda:python3.6 cloneintobucket.handler '{"local": "true"}'`

echo 'Waiting for logs to become available'
sleep 5
docker logs ${CONTAINER_NAME}

docker exec --interactive --tty ${CONTAINER_ID} /bin/bash
