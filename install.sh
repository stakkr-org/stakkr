#!/bin/bash
set -e

echo "Cleaning the old virtualenv"
rm -rf *.egg-info
rm -rf ${PWD##*/}_lamp


echo "Installing various python packages"
sudo apt-get -y install python3-pip python3-setuptools python3-virtualenv virtualenv > /dev/null
sudo pip3 install -q --upgrade pip > /dev/null
sudo pip3 install -q autoenv > /dev/null

echo ""
echo "If you want to automatically load the current virtualenvironment, check that you have something like "
echo "'echo \"source `which activate.sh`\"' in your ~/.bashrc"
echo ""

echo "Creating the virtualenv"
virtualenv -p /usr/bin/python3 ${PWD##*/}_lamp > /dev/null
source ${PWD##*/}_lamp/bin/activate > /dev/null
pip3 install click clint > /dev/null
pip3 install -e . > /dev/null

echo "Leaving the virtualenv. To enter it again do : "
echo "   source \${PWD##*/}_lamp/bin/activate"
deactivate > /dev/null
