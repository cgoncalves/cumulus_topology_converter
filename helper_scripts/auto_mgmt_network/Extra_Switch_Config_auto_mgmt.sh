#!/bin/bash

echo "############################################"
echo "  Running Extra_Switch_Config_auto_mgmt.sh"
echo "############################################"
sudo su

cat <<EOT > /etc/network/interfaces
auto lo
iface lo inet loopback

auto vagrant
iface vagrant inet dhcp

auto eth0
iface eth0 inet dhcp

EOT

echo "#################################"
echo "   Finished"
echo "#################################"
