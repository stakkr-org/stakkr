#!/bin/bash
echo "Installing various python packages"
sudo apt-get -y install python3-pip python3-setuptools python3-virtualenv > /dev/null

echo "Creating the virtualenv"
virtualenv -p /usr/bin/python3 ${PWD##*/}_lamp > /dev/null
source ${PWD##*/}_lamp/bin/activate > /dev/null
pip3 install click > /dev/null
pip3 install -e . > /dev/null

echo "Leaving the virtualenv. To enter it again do : "
echo "source \${PWD##*/}_lamp/bin/activate"
deactivate > /dev/null
