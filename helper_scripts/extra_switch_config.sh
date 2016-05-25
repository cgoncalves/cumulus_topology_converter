#!/bin/bash

echo "#################################"
echo "  Running Extra_Switch_Config.sh"
echo "#################################"
sudo su

echo -e "\n\nauto lo" > /etc/network/interfaces
echo -e "iface lo inet loopback\n\n" >> /etc/network/interfaces

echo -e "\n\nauto vagrant" >> /etc/network/interfaces
echo -e "iface vagrant inet dhcp\n\n" >> /etc/network/interfaces

#echo -e "\n\nauto eth0" >> /etc/network/interfaces
#echo -e "iface eth0 inet dhcp\n\n" >> /etc/network/interfaces

#add line to support bonding inside virtualbox VMs
#sed -i '/.*iface swp.*/a\    #required for traffic to flow on Bonds in Vbox VMs\n    post-up ip link set $IFACE promisc on' /etc/network/interfaces

echo "#################################"
echo "   Finished"
echo "#################################"
