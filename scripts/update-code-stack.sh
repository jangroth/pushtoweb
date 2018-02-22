#!/bin/bash -eux

cd ../infra

aws cloudformation update-stack \
  --stack-name ptw-code \
  --template-body file://code-infra.yml \
  --capabilities CAPABILITY_IAM
