#!/bin/bash -eux

cd ../infra
aws cloudformation delete-stack --stack-name ptw-code
