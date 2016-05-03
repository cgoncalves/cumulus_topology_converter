#!/bin/bash

echo "#################################"
echo "   Running OOB_Switch_Config.sh"
echo "#################################"
sudo su

echo -e "auto vagrant" > /etc/network/interfaces
echo -e "iface vagrant inet dhcp\n" >> /etc/network/interfaces

####### Custom Stuff

# Config for OOB Switch
echo -e "auto lo" >> /etc/network/interfaces
echo -e "iface lo inet loopback\n" >> /etc/network/interfaces
#echo -e "auto eth0" >> /etc/network/interfaces
#echo -e "iface eth0\n" >> /etc/network/interfaces
echo -e "% for i in range(1, 49):" >> /etc/network/interfaces
echo -e "auto swp\${i}" >> /etc/network/interfaces
echo -e "iface swp\${i}" >> /etc/network/interfaces
echo -e "% endfor\n" >> /etc/network/interfaces
echo -e "auto bridge" >> /etc/network/interfaces
echo -e "iface bridge" >> /etc/network/interfaces
echo -e "address 192.168.252.1/24" >> /etc/network/interfaces
echo -e "bridge-ports glob swp1-48" >> /etc/network/interfaces
echo -e "bridge-stp on" >> /etc/network/interfaces

echo "#################################"
echo "   Finished "
echo "#################################"



