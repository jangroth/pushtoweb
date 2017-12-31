#!/bin/bash -eux

cd ..
aws cloudformation update-stack \
  --stack-name ptw-web \
  --template-body file://web-infra.yml \
  --parameters file://scripts/parameters.json \
  --capabilities CAPABILITY_IAM
