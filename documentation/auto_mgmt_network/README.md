#Automated Management Network Builder

##Table of Contents
* [Writing a Topology.dot File](#writing-a-topologydot-file)
* [Default Automatic Behaviors](#default-automatic-behaviors)
* [Implementation Details](#implementation-details)
* [Sample Output](#sample-output)


The '-c' option can be used and TC will automatically build a management network for your topology complete with an Out of Band Managment Server (oob-mgmt-server) an Out of Band management switch (oob-mgmt-switch) and every other device's eth0 port connected to a single bridge on the oob-mgmt-switch device. Port swp1 on the oob-mgmt-switch will always connect to the oob-mgmt-server.


![Automatically Built Devices and Links](./automated_mgmt_network.png)

###Writing a Topology.dot File
Here is a sample topology.dot file that works with the automated management network builder feature. Notice that mgmt_ip is specified for various nodes, these will be the eth0 ip addresses that will be mapped to DHCP entries on the oob-mgmt-server.

```
graph dc1 {
 "oob-mgmt-server" [function="oob-server" mgmt_ip="192.168.200.254"]
 "leaf1" [function="leaf" mgmt_ip="192.168.200.10"]
 "leaf2" [function="leaf" mgmt_ip="192.168.200.20"]
   "leaf1":"swp1" -- "leaf2":"swp1"
   "leaf1":"swp2" -- "leaf2":"swp2"
   "leaf1":"swp3" -- "leaf2":"swp3"
   "leaf1":"swp4" -- "leaf2":"swp4"
}
```

When used with another example topology.dot file like the one below, a default mgmt_ip of 192.168.200.254 will be assumed on the oob-mgmt-server and DHCP will be handed out in a first-come-first-serve fashion from 192.168.200.201-192.168.200.250 in the 192.168.200.0/24 subnet for all eth0 ports on the leaves.

```
graph dc1 {
 "leaf1" [function="leaf"]
 "leaf2" [function="leaf"]
   "leaf1":"swp1" -- "leaf2":"swp1"
   "leaf1":"swp2" -- "leaf2":"swp2"
   "leaf1":"swp3" -- "leaf2":"swp3"
   "leaf1":"swp4" -- "leaf2":"swp4"
}
```

###Default Automatic Behaviors
* OOB-mgmt-server is created using Ubuntu1604
* OOB-mgmt-switch is created using the default CumulusCommunity/cumulus-vx image
  * A link between the oob-mgmt-server:mgmt_net <--> oob-mgmt-switch:swp1 is created
  * A link from Eth0 of each device is created to the next available port on oob-mgmt-switch starting with swp2
* DHCP Server installed on oob-mgmt-server
  * If "mgmt_ip=" is specified on the oob-mgmt-server that IP address (multiple can be specified in CSV format) will be applied to the mgmt_net interface. DHCP will be configured for each of the mgmt_ip subnets as /24 class C networks with the 201-250 addresses being reserved for generic DHCP. 
    * It is recommended to have your nodes configured with a last octet mgmt_ip between 1-200
    * It is recommended to have your oob-mgmt-server mgmt_ip configured with .254 as the last octet
  * If "mgmt_ip=" is not specified in the oob-mgmt-server node definition, a default value of 192.168.200.254 is assumed and DHCP will be handled using the 192.168.200.0/24 subnet (192.168.200.201-192.168.200.250).
  * If "mgmt_ip=" is specified in node definitions, a MAC entry will be created for the Eth0 port on each device associated with the provided "mgmt_ip" address for that node.
* Ansible Installed on oob-mgmt-server
  * Ansible Hostfile prebuilt and installed to /etc/ansible/hosts based on nodes and management IPs
* /etc/hosts file pre-built on oob-mgmt-server


###Implementation Details
In order for the create mgmt 

###Sample Output
From the output below it is possible to see the managment links being automatically created. If you use the '-v' option you will see even more as all of the extra individual template files are rendered.

```
python ./topology_converter.py ./examples/2switch_auto_mgmt.dot -c

######################################
          Topology Converter
######################################
  adding mgmt links:
    oob-mgmt-switch:swp1 (mac: 44:38:39:00:00:09) --> oob-mgmt-server:mgmt_net (mac: 44:38:39:00:00:0a)     network_string:net6
    oob-mgmt-switch:swp2 (mac: 44:38:39:00:00:0b) --> leaf1:eth0 (mac: 44:38:39:00:00:0c)     network_string:net7
    oob-mgmt-switch:swp3 (mac: 44:38:39:00:00:0d) --> leaf2:eth0 (mac: 44:38:39:00:00:0e)     network_string:net8
>> DEVICE: oob-mgmt-server
     code: boxcutter/ubuntu1604
     memory: 512
     function: oob-server
     mgmt_ip: 192.168.200.254
     hostname: oob-mgmt-server
     config: ./helper_scripts/auto_mgmt_network/OOB_Server_Config_auto_mgmt.sh
       LINK: mgmt_net
               remote_device: oob-mgmt-switch
               mac: 44:38:39:00:00:0a
               network: net6
               remote_interface: swp1
>> DEVICE: oob-mgmt-switch
     code: CumulusCommunity/cumulus-vx
     memory: 512
     function: oob-switch
     hostname: oob-mgmt-switch
     config: ./helper_scripts/auto_mgmt_network/OOB_Switch_Config.sh
       LINK: swp1
               remote_device: oob-mgmt-server
               mac: 44:38:39:00:00:09
               network: net6
               remote_interface: mgmt_net
       LINK: swp2
               remote_device: leaf1
               mac: 44:38:39:00:00:0b
               network: net7
               remote_interface: eth0
       LINK: swp3
               remote_device: leaf2
               mac: 44:38:39:00:00:0d
               network: net8
               remote_interface: eth0
>> DEVICE: leaf1
     code: CumulusCommunity/cumulus-vx
     memory: 512
     function: leaf
     mgmt_ip: 192.168.200.10
     hostname: leaf1
     config: ./helper_scripts/auto_mgmt_network/Extra_Switch_Config_auto_mgmt.sh
       LINK: eth0
               remote_device: oob-mgmt-switch
               mac: 44:38:39:00:00:0c
               network: net7
               remote_interface: swp2
       LINK: swp1
               remote_device: leaf2
               mac: 44:38:39:00:00:07
               network: net4
               remote_interface: swp1
       LINK: swp2
               remote_device: leaf2
               mac: 44:38:39:00:00:01
               network: net1
               remote_interface: swp2
       LINK: swp3
               remote_device: leaf2
               mac: 44:38:39:00:00:05
               network: net3
               remote_interface: swp3
       LINK: swp4
               remote_device: leaf2
               mac: 44:38:39:00:00:03
               network: net2
               remote_interface: swp4
>> DEVICE: leaf2
     code: CumulusCommunity/cumulus-vx
     memory: 512
     function: leaf
     mgmt_ip: 192.168.200.20
     hostname: leaf2
     config: ./helper_scripts/auto_mgmt_network/Extra_Switch_Config_auto_mgmt.sh
       LINK: eth0
               remote_device: oob-mgmt-switch
               mac: 44:38:39:00:00:0e
               network: net8
               remote_interface: swp3
       LINK: swp1
               remote_device: leaf1
               mac: 44:38:39:00:00:08
               network: net4
               remote_interface: swp1
       LINK: swp2
               remote_device: leaf1
               mac: 44:38:39:00:00:02
               network: net1
               remote_interface: swp2
       LINK: swp3
               remote_device: leaf1
               mac: 44:38:39:00:00:06
               network: net3
               remote_interface: swp3
       LINK: swp4
               remote_device: leaf1
               mac: 44:38:39:00:00:04
               network: net2
               remote_interface: swp4

############
SUCCESS: Vagrantfile has been generated!
############

DONE!

```


