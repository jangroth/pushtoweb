#!/bin/bash -eux

cd ../infra
aws cloudformation create-stack --stack-name ptw-code --template-body file://code-infra.yml
