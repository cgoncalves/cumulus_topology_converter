#!/bin/bash

#################################################
# Zero Touch Provisioning for NetQ Cloud (OPTA)
#################################################
#CUMULUS-AUTOPROVISIONING

# Enable Script Failure on errors and Enable Per Command Logging
set -x 
set -e

echo "# Waiting for NCLU to finish starting up..."
last_code=1
while [ "1" == "$last_code" ]; do
    net show interface &> /dev/null
    last_code=$?
done

# Setup NTP
sed -i '1s/^/tinker panic 0\n/' /etc/ntp.conf
sed -i 's/^interface listen eth0/#interface listen eth0/g' /etc/ntp.conf
sudo systemctl restart ntp

SSH_URL="http://192.168.200.1/authorized_keys"
#Setup SSH key authentication for Ansible
mkdir -p /home/cumulus/.ssh
wget -O /home/cumulus/.ssh/authorized_keys $SSH_URL

#add cumulus user for passwordless sudo
echo "cumulus ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/10_cumulus

logger "ZTP Finished" -t "NetQ ZTP"

exit 0

