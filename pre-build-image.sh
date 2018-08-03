#!/usr/bin/env sh
set -e

rm -rf env/
python3.6 -m venv env
source env/bin/activate
pip3 install requests
find . -name "*.pyc" -exec rm -f {} \;
#docker build . -t sdenel/proxy-add-base-href
