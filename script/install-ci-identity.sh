#!/bin/bash
set -euo pipefail

cd $(dirname $0)
mkdir -p ~/.ssh/ci-identity

# allow overwriting ci-identity if one already existed
chmod -R 700 ~/.ssh/ci-identity

cp config ~/.ssh/config

cp -r ci-identity ~/.ssh/

# protect keys from public access
chmod 400 ~/.ssh/ci-identity/* 