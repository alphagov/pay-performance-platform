#!/bin/bash

set -eo pipefail

VERSION="0.0.1"

IFS=$'\n\t'

if [ -z "$1" ]; then
  echo "Usage: $0 <S3_BUCKET>"
  exit 1
fi

S3_BUCKET=${1}
S3_KEY=${2:-pay-performance-platform}

ARTIFACT="${S3_KEY}"-"${VERSION}".zip

TARGET=s3://"${S3_BUCKET}"/"${ARTIFACT}"
TMP_DIR=$(mktemp -d /tmp/lambda-XXXXXX)
ZIPFILE="${TMP_DIR}"/"${ARTIFACT}"

virtualenv venv
. ./venv/bin/activate
./venv/bin/python ./venv/bin/pip install -r requirements.txt

cp ./*.py ./*.txt ./*.pyc $TMP_DIR
cp -R ./venv/lib/python2.7/site-packages/* $TMP_DIR

set -u

cd $TMP_DIR
zip -mr "${ZIPFILE}" .

aws s3 cp --acl=private ${ZIPFILE} ${TARGET}

rm -rf ${TMP_DIR}
