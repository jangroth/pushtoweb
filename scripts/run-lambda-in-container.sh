#!/bin/bash -eux

parent_folder=`dirname $(pwd)`

docker run --rm \
    --volume ${parent_folder}/scripts:/scripts:ro \
    --volume ${parent_folder}/code:/code:ro \
    --volume ${parent_folder}/build:/build \
    ptw:lambdapackage /bin/bash -c '/scripts/package.sh && cd /build && python3 cloneintobucket.py'