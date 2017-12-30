#!/bin/bash -eux

cd ..
aws cloudformation delete-stack --stack-name ptw-infrastructure
