#!/bin/bash -eux

cd ..
aws cloudformation update-stack --stack-name ptw-code --template-body file://code-infra.yml --capabilities CAPABILITY_IAM
