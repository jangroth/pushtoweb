#!/bin/bash -eux

cd ..
aws cloudformation update-stack --stack-name ptw-web --template-body file://web-infra.yml --capabilities CAPABILITY_IAM