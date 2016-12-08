#!/bin/bash

echo "#################################"
echo "   Running OOB_Switch_Config.sh"
echo "#################################"
sudo su

# Config for OOB Switch
cat <<EOT > /etc/network/interfaces
auto lo
iface lo inet loopback

auto vagrant
iface vagrant inet dhcp

auto eth0
iface eth0 inet dhcp

% for i in range(1, 49):
auto swp\${i}
iface swp\${i}
% endfor

auto bridge
iface bridge inet dhcp
    bridge-ports glob swp1-48
    bridge-stp on

EOT


echo "#################################"
echo "   Finished "
echo "#################################"
