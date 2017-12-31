#!/bin/bash -eux

source config.src

cd ../lambda
zip pushtobucket.zip pushtobucket.py

aws s3 cp pushtobucket.zip s3://${CODE_BUCKET_NAME}/ --storage-class REDUCED_REDUNDANCY
aws s3api list-object-versions --bucket ${CODE_BUCKET_NAME} --max-items 1 | grep 'VersionId'
