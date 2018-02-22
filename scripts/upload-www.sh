#!/bin/bash -eux

source config.src

cd ../infra
aws s3 cp www s3://${WEB_BUCKET_NAME}/ --recursive --storage-class REDUCED_REDUNDANCY
