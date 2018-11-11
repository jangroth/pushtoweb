#!/bin/bash -eux

docker build --tag ptw:lambdapackage --file Dockerfile_package_lambda .