#!/bin/bash -eux

docker build --tag ptw:lambdalocal --file Dockerfile_package_lambda .