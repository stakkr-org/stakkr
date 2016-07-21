#!/bin/bash
sudo apt-get -y install python3-pip python3-setuptools python3-virtualenv
virtualenv -p /usr/bin/python3 ${PWD##*/}_lamp
source ${PWD##*/}_lamp/bin/activate
pip3 install -e .
deactivate
