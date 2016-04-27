#!/bin/bash

#This file is transferred to a Debian/Ubuntu Host and executed to re-map interfaces
#Extra config COULD be added here but I would recommend against that to keep this file standard.
echo "#################################"
echo "  Running Extra_Server_Config.sh"
echo "#################################"
sudo su

#remove cloud-init software
#apt-get purge cloud-init -y

#Replace existing network interfaces file
#echo -e "auto lo" > /etc/network/interfaces
#echo -e "iface lo inet loopback\n\n" >> /etc/network/interfaces
#echo -e  "source /etc/network/interfaces.d/*.cfg\n" >> /etc/network/interfaces

#Add vagrant interface
#echo -e "\n\nauto vagrant" > /etc/network/interfaces.d/vagrant.cfg
#echo -e "iface vagrant inet dhcp\n\n" >> /etc/network/interfaces.d/vagrant.cfg

#echo -e "\n\nauto eth0" > /etc/network/interfaces.d/eth0.cfg
#echo -e "iface eth0 inet dhcp\n\n" >> /etc/network/interfaces.d/eth0.cfg


which yum
if [ "$?" == "0" ]; then
    /usr/bin/dnf install python -y
    echo -e "DEVICE=vagrant\nBOOTPROTO=dhcp\nONBOOT=yes" > /etc/sysconfig/network-scripts/ifcfg-vagrant
fi


echo "#################################"
echo "   Finished"
echo "#################################"
