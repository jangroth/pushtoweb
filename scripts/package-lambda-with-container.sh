#!/bin/bash -eux

parent_folder=`dirname $(pwd)`

docker run --rm \
    --volume ${parent_folder}/scripts:/scripts:ro \
    --volume ${parent_folder}/code:/code:ro \
    --volume ${parent_folder}/build:/build \
    --user 1000:1000 \
    ptw:lambdapackage /scripts/package.sh