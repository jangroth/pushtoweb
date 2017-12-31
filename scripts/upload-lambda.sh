#!/bin/bash -eux

source config.src

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
LAMBDA_DIR="${SCRIPT_DIR}/../lambda"
DEPENDENCY_DIR="${SCRIPT_DIR}/../venv3/lib/python3.5/site-packages"
DIST_DIR="${LAMBDA_DIR}/dist"

rm -f "${LAMBDA_DIR}/cloneintobucket.zip"
rm -rf $DIST_DIR
mkdir -p $DIST_DIR

cp "${LAMBDA_DIR}/cloneintobucket.py" $DIST_DIR
cp -r "${DEPENDENCY_DIR}/." $DIST_DIR
rm -rf ${DIST_DIR}/boto*
rm -rf ${DIST_DIR}/s3*
rm -rf $DIST_DIR/__pycache__

pushd $DIST_DIR
zip -r $LAMBDA_DIR/cloneintobucket.zip .
popd

unzip -l $LAMBDA_DIR/cloneintobucket.zip

aws s3 cp "${LAMBDA_DIR}/cloneintobucket.zip" s3://${CODE_BUCKET_NAME}/ --storage-class REDUCED_REDUNDANCY
aws s3api list-object-versions --bucket ${CODE_BUCKET_NAME} --max-items 1 | grep 'VersionId'
