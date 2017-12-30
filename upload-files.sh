#!/bin/bash -eux

aws s3 cp www s3://ptw-infrastructure-websitebucket-k0aguzr8adez/ --recursive --storage-class REDUCED_REDUNDANCY
