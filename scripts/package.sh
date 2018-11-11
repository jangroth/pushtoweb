#!/usr/bin/bash -eux

rm -rf /build/*
cp /code/cloneintobucket.py /build/
cp /code/binaries/* /build/
cp -r /code/templates/ /build/

pip install -r /code/requirements.txt -t /build

cd /build
zip -r /build/cloneintobucket.zip ./*