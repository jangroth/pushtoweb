#!/bin/bash -eux

aws cloudformation create-stack --stack-name ptw-infrastructure --template-body file://infrastructure.yml
