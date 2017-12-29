#!/bin/bash -eux

aws cloudformation update-stack --stack-name ptw-infrastructure --template-body file://infrastructure.yml
