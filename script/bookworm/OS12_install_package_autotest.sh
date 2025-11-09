#!/bin/bash

# login as root user
echo password | sudo -S 

# install package in the system
REQUIRED_PKG="python3-tk python3-dev gcc tesseract-ocr scrot wget unzip python3-venv python3-pip python3-apt python3-full"
for i in $REQUIRED_PKG; do
    PKG_OK=$(dpkg-query -W --showformat='${Status}\n' $i|grep "install ok installed")
    echo Checking for $i: $PKG_OK
    if [ "" = "$PKG_OK" ]; then
        echo "No $i. Setting up $i."
        sudo apt-get update
        sudo apt-get --yes install $i
    fi
done


# Create virtual environment
python3 -m venv /home/vimec/venv/

# Activate virtual environment
source /home/vimec/venv/bin/activate

# Upgrade pip inside venv
pip install --upgrade pip

# Install pip packages from requirements.txt
pip install -r OS12_requirements.txt

echo "Python package installation complete!"

# Update authorized_keys for vimec login
cd /home/vimec/v-center-testing/script/
sh install-ci-identity.sh
cp ~/.ssh/ci-identity/id_ed25519.pub ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys