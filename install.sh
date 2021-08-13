#!/bin/bash

git submodule update --init mozilla-ca

echo "Ubuntu 20.04 LTS only supported."

sudo apt-get update
sudo apt-get install -y python3.8-venv python3-distutils

python3 -m venv venv

ln -s venv/bin/activate .

. ./activate

python -m pip install --upgrade pip
python -m pip install wheel

python -m pip install --extra-index-url https://pypi.achicoin.org/simple/ miniupnpc==2.2.2
python -m pip install -e . --extra-index-url https://pypi.achicoin.org/simple/

echo ""
echo "Achi blockchain install.sh complete."
echo ""
echo "Type '. ./activate' and then 'achi init' to begin."
