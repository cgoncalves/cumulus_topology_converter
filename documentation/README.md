#Topology Converter Documentation

##Table of Contents
* [Glossary](#glossary)
* [Features](#features)
* [Installation](#installation)
* [Using Topology Converter](#using-topology-converter)
  * [The Basic Workflow](#the-basic-workflow)
  * [What is it doing?](#what-is-happening-when-you-run-topology-converter)
  * [Functional Defaults](#functional-defaults)
* [Optional Features](#optional-features)
  * [Providers](#providers)
  * [Faked Devices](#faked-devices)
  * [Boot Ordering](#boot-ordering)
  * [MAC Address Handout](#mac-handout)
  * [Ansible Hostfile Generation](#ansible-hostfile-generation)
  * [Inter-Hypervisor Simulation](#inter-hypervisor-simulation)
  * [Custom Templates](#custom-templates)
  * [Passthrough Attributes](#passthrough-attributes)
  * [Provisioning Scripts](#provisioning-scripts)
  * [Specifying an Ansible Playbooks](#ansible-playbooks)
  * [Debugging Mode](#debugging-mode)
* [Miscellaneous Info](#miscellaneous-info)
* [Example Topologies](#example-topologies)
  * [The Reference Topology](#the-reference-topology)
  * [2 Switch](#2-switch-topology)
  * [1 Switch 1 Server](#1-switch-1-server-topology)
  * [2 Switch 1 Server](#2-switch-1-server-topology)
  * [3 Switch Circular](#3-switch-circular-topology)


```
                                                                       +---------+
                                                                  +--> | LibVirt |
                    +----------------------+                      |    +---------+
+--------------+    |                      |    +--------------+  |
| Topology.dot +--> |  Topology-Converter  +--> | Vagrantfile  +--+
+--------------+    |                      |    +--------------+  |
                    +----------------------+                      |    +------------+
                                                                  +--> | VirtualBox |
                                                                       +------------+
```

##Glossary:
* **Topology File** -- Usually a file ending in the ".dot" suffix. This file describes the network topology link-by-link. Written in https://en.wikipedia.org/wiki/DOT_(graph_description_language). This file can be the same one used as part of the [Perscriptive Topology Manager (PTM) feature](https://docs.cumulusnetworks.com/display/DOCS/Prescriptive+Topology+Manager+-+PTM) in Cumulus Linux.
* **Provider** -- similar to a hypervisor, providers are Vagrant's term for the device that is either directoy hosting the VM (virtualbox) or the subsystem that vagrant is communicating with to further orchestratrate the creation of the VM (libvirt)
* **Interface Remapping** -- Interface remapping is the process by which interfaces are renamed to match the interfaces specified in the topology file. Interface Remapping uses UDEV rules that are orchestrated in the Vagrantfile and applied by the apply_udev.py script on the machines under simulation. This process allows a device in a topologyfile to simulate ports like "swp49" without having to simulate ports swp1-48. See the "[Miscellaneous Info](#miscellaneous-info)" Section for additional information.


##Features
* Converts a topology file "topology.dot" into a Vagrantfile
* 1 file is modified by the user to create a suitable Vagrantfile (topology.dot)
* Handles interface remapping on Vx instances (and hosts) to match the interfaces used in the provided topology file
* Removes extra Ruby-based logic from the Vagrantfile making a simple human-readable output
* Can generate Vagrantfiles that contain servers and switches and anything else that can be found in a Vagrant Box image
* Does not require Vagrant/Virtualbox/libvirt to be installed to create the Vagrantfile
* Supports the Virtualbox and Libvirt Vagrant Providers (Hypervisors)

##Installation

###Ubuntu
Both 16.04 and 14.04.

```
sudo apt install python-pip
sudo pip install --upgrade pip
sudo pip install setuptools
sudo pip install pydotplus
sudo pip install jinja2
```

###Mac


```
sudo easy_install pip
sudo pip install --upgrade pip
sudo pip install setuptools
sudo pip install pydotplus
sudo pip install jinja2
```


##Using Topology Converter
To use Topology Converter [TC] you need to work with one file: topology.dot
 
The actual name of the topology file is irrelevant. Your "topology.dot" file could be named "HAPPYHAPPYJOYJOY.dot" and that would be just fine.
 
###The Basic Workflow
**1). Create a Topology File** 
Create a topology.dot file or borrow a provided ".dot" file from the "topology_converter/examples/" directory
In this example, we'll work with the topology_converter / examples / 2switch_1server.dot file shown below:

```
graph dc1 {
 "leaf1" [function="leaf" os="CumulusCommunity/cumulus-vx" memory="200" config="./helper_scripts/extra_switch_config.sh"]
 "leaf2" [function="leaf" os="CumulusCommunity/cumulus-vx" memory="200" config="./helper_scripts/extra_switch_config.sh"]
 "server1" [function="host" os="boxcutter/ubuntu1404" memory="400" ubuntu=True config="./helper_scripts/extra_server_config.sh"]
   "leaf1":"swp40" -- "leaf2":"swp40"
   "leaf1":"swp50" -- "leaf2":"swp50"
   "server1":"eth1" -- "leaf1":"swp1"
   "server1":"eth2" -- "leaf2":"swp1"
}
```

Place this topology.dot file in the same directory as topology_converter.py (or any subdirectory beneath the directory which contains topology_converter.py)

**2). Convert it to a Vagrantfile**

```
      $ python ./topology_converter.py ./topology.dot
```

or if using Libvirt:


```
      $ python ./topology_converter.py ./topology.dot -p libvirt
```

**3). Start the Simulation**

```
      $ vagrant up
```

or if using Libvirt:


```
      $ vagrant up --provider=libvirt
```

###What is happening when you run Topology Converter?
1. When topology_converter (TC) is called, TC reads the provided topology file line by line and learns information about each node and each link in the topology.
2. This information is stored in a variables datastructure. (View this datastructure using the "python ./topology_converter.py [topology_file] -dd" option)
3. A jinja2 template "Vagrantfile.j2" (stored in the /templates directory) is used to render a Vagrantfile based on the variables datastructure.

###Functional Defaults
Functional defaults provide basic options for memory and OS when using pre-defined functions. Presently the functional defaults are defined as follows but can be overwritten by manually specifying the associated attribute.

**For Functions:** "oob-switch" "exit" "spine" "leaf"

**Functional Defaults are:**
* os="CumulusCommunity/cumulus-vx"
* memory="300"

**For Functions:** "oob-server" and "host"

**Functional Defaults are:**
* os="boxcutter/ubuntu1604"
* memory="500"

Note: See more information about what functions are used for in the [Faked Devices](#faked-devices) and [Boot Ordering](#boot-ordering) sections.


##Optional Features (Everything Else)

###Providers
Topology Converter supports the use of two providers, Virtualbox and Libvirt (/w KVM). Virtualbox is the default provider. 

To use Libvirt/KVM specify the "-p libvirt" option

```
-p PROVIDER, --provider PROVIDER
                      specifies the provider to be used in the Vagrantfile,
                      script supports "virtualbox" or "libvirt", default is
                      virtualbox.
```


###Faked Devices
In virtual environments it may not always be possible to simulate every single device due to memory restrictions, interest, proprietary OSes etc. Faked devices give Topology Converter a way to know that a device in a topology.dot file is not actually going to be simulated. However when a faked device is connected to a real device the real device MUST create an interface as if the faked device was actually present.
Creating the interface allows for the simulation of interface configuration that would face the faked device. If no interface was present, the interface configuration may fail which could inhibit automation tooling tests and ultimately provide a less accurate simulation. To specify that a device is to be faked, add it to the "function" attribute of the node definition in the topology file.

```
graph dc1 {
 "leaf1" [function="fake"]
 "leaf2" [function="leaf" os="CumulusCommunity/cumulus-vx" memory="200" config="./helper_scripts/extra_switch_config.sh"]
   "leaf1":"swp40" -- "leaf2":"swp40"
   "leaf1":"swp50" -- "leaf2":"swp50"
}
```

###Boot Ordering
Boot ordering is accomplished in Virtualbox by using the "function" attribute of the node:
Order:

1). function="oob-server"

2). function="oob-switch"

3). function="exit"

4). function="spine"

5). function="leaf"

6). function="host"

7). function= ANYTHING ELSE

The boot order directly relates to the location of the VM's definition in the generated Vagrantfile... VMs at the top of the Vagrantfile will boot first.

###MAC Handout
If a MAC address is not specified using the format shown below then it will be auto assigned starting from the address [ 44:38:39:00:00:00 ] which is Cumulus' private MAC address range.

```
graph dc1 {
 "leaf1" [function="leaf" os="CumulusCommunity/cumulus-vx" memory="200" config="./helper_scripts/extra_switch_config.sh"]
 "leaf2" [function="leaf" os="CumulusCommunity/cumulus-vx" memory="200" config="./helper_scripts/extra_switch_config.sh"]
   "leaf1":"swp1" -- "leaf2":"swp1" [ left_mac="44:38:39:1eaf:11", right_mac="44:38:39:1eaf:21"]
   "leaf1":"swp2" -- "leaf2":"swp2" [ left_mac="44:38:39:1eaf:12", right_mac="44:38:39:1eaf:22"]
   "leaf1":"swp3" -- "leaf2":"swp3" [ left_mac="44:38:39:1eaf:13", right_mac="44:38:39:1eaf:23"]
   "leaf1":"swp4" -- "leaf2":"swp4" [ left_mac="44:38:39:1eaf:14", right_mac="44:38:39:1eaf:24"]
}
```

At the conclusion of the run, the MAC address to interface mapping will be written in CSV format to the dhcp_mac_map file that lives in the same directory as topology_converter.py. The format for that file is as follows:

```
#Device,interface,MAC
leaf1,swp1,4438391eaf11
leaf1,swp2,4438391eaf12
leaf1,swp3,4438391eaf13
leaf1,swp4,4438391eaf14
leaf2,swp1,4438391eaf21
leaf2,swp2,4438391eaf22
leaf2,swp3,4438391eaf23
leaf2,swp4,4438391eaf24
``` 

###Ansible Hostfile Generation
When the "-a" option is specified, Ansible hostfiles will be generated by Vagrant. TC will create a dummy playbook in the helper_scripts directory (called: empty_playbook.yml) with one task (shell: "uname -a") which will force Vagrant to create a hostfile which can be used to run other Ansible playbooks later if you chose. TC will also create an "ansible.cfg" file for use with Ansible.

```
-a, --ansible-hostfile
                      When specified, ansible hostfile will be generated
                      from a dummy playbook run.
```


###Inter-Hypervisor Simulation
![InterHypervisor Simulation](interhypervisor_simulation.png)

It is possible to strech simulations across an L3 fabric to place different simulated devices on different physical nodes. This can only be done using the Libvirt provider option and only with libvirt v 1.2.20+ which contains the relevent patches to support the UDP tunnel infrastructure which Cumulus engineers contributed to the libvirt codebase. This is possible using the "tunnel_ip" node-parameter. When not specified for a libvirt simulation the default of 127.0.0.1 is assumed for a fully contained local simulation.

```
graph dc1 {
 "leaf1" [function="leaf" os="CumulusCommunity/cumulus-vx" memory="300" config="./helper_scripts/extra_switch_config.sh" tunnel_ip="192.168.1.1"]
 "leaf2" [function="leaf" os="CumulusCommunity/cumulus-vx" memory="300" config="./helper_scripts/extra_switch_config.sh" tunnel_ip="192.168.1.2"]
   "leaf1":"swp11" -- "leaf2":"swp1" [ left_mac="44:38:39:1e:af:11", right_mac="44:38:39:1e:af:21"]
   "leaf1":"swp2" -- "leaf2":"swp2" [ left_mac="44:38:39:1e:af:12", right_mac="44:38:39:1e:af:22"]
   "leaf1":"swp33" -- "leaf2":"swp3" [ left_mac="44:38:39:1e:af:13", right_mac="44:38:39:1e:af:23"]
   "leaf1":"swp4" -- "leaf2":"swp4" [ left_mac="44:38:39:1e:af:14", right_mac="44:38:39:1e:af:24"]
}
```


###Custom Templates
TC works by reading information from a topology file into variables which are then used to populate a Jinja2 template for the Vagrantfile (called: ./templates/Vagrantfile.j2). TC allows you to specify additional templates that can be filled in using the same information from the topology file.

To see a list of the variables that will be passed to a template use the "-dd" which is short for "display datastructure" option.

```
python ./topology_converter.py ./examples/2switch.dot -dd

```

To specify a custom template use the "-t" option: 

```
  -t [templatefile] [rendered_output_location], --template TEMPLATE TEMPLATE
                        Specify an additional jinja2 template and a
                        destination for that file to be rendered to.

```

###Passthrough Attributes
When working with custom templates or when modifying the included Vagrantfile template (called: ./templates/Vagrantfile.j2) it may be useful to provide additional parameters to populate variables in your customized template. By default any variable specified at the node level is automatically passed through to the templates whether or not TC actually uses it. This allows for maximum flexibility for end-users to add custom information about nodes and attributes.

**Note: for links it is possible to override the attributes generated for the link by TC since passthrough attributes are applied last. One could use this to manually specify a particular network number for the virtualbox provider. For attributes specified on links, any attrubutes which are not "left_mac" or "right_mac" will be applied to both ends of the link.**

Node-Based Passthrough Attribute shown below: "testattr"

Link-Based Passthrough Attribute shown below: "newattribute"


```
graph dc1 {
 "leaf1" [function="leaf" os="CumulusCommunity/cumulus-vx" memory="200" config="./helper_scripts/extra_switch_config.sh"]
 "leaf2" [function="leaf" os="CumulusCommunity/cumulus-vx" memory="200" config="./helper_scripts/extra_switch_config.sh"]
 "server1" [function="host" os="boxcutter/ubuntu1404" memory="400" ubuntu=True config="./helper_scripts/extra_server_config.sh" testattr="123456"]
   "leaf1":"swp40" -- "leaf2":"swp40"
   "leaf1":"swp50" -- "leaf2":"swp50" [newattribute="some value"]
   "server1":"eth1" -- "leaf1":"swp1"
   "server1":"eth2" -- "leaf2":"swp1"
}
```


###Provisioning Scripts
Scripts can be specified for execution on the end host using the "config=" node attribute in a topology file. In the example below, a "custom_script.sh" is used to provision the leaf1 device.

```
graph dc1 {
 "leaf1" [function="leaf" os="CumulusCommunity/cumulus-vx" memory="200" config="./helper_scripts/custom_script.sh"]
 "leaf2" [function="leaf" os="CumulusCommunity/cumulus-vx" memory="200" ]
 "server1" [function="host" os="boxcutter/ubuntu1404" memory="400" ubuntu=True ]
   "leaf1":"swp40" -- "leaf2":"swp40"
   "leaf1":"swp50" -- "leaf2":"swp50"
   "server1":"eth1" -- "leaf1":"swp1"
   "server1":"eth2" -- "leaf2":"swp1"
}
```

###Ansible Playbooks
Similar to the above option, provisioning and configuration can be performed by specifying a node-specific Ansible Playbook. Specifiying a playbook here will call the Vagrant Ansible provisioner and force Vagrant to generate an Ansible hostfile.

```
graph dc1 {
 "leaf1" [function="leaf" os="CumulusCommunity/cumulus-vx" memory="200" playbook="main.yml"]
 "leaf2" [function="leaf" os="CumulusCommunity/cumulus-vx" memory="200" ]
 "server1" [function="host" os="boxcutter/ubuntu1404" memory="400" ubuntu=True ]
   "leaf1":"swp40" -- "leaf2":"swp40"
   "leaf1":"swp50" -- "leaf2":"swp50"
   "server1":"eth1" -- "leaf1":"swp1"
   "server1":"eth2" -- "leaf2":"swp1"
}
```


###Debugging Mode 
Use the -v option.

```
-v, --verbose         enables verbose logging mode
```

###synced_folder=False
Documentation coming soon!

 
##Miscellaneous Info
* When simulating with Vagrant, vagrant will usually create two extra interfaces in addition to all of the interfaces that are needed for simulation. The reason for this behavior is unknown at this point in time.
* When simulating with Ubuntu, specify the "ubuntu=True" node-level attribute in the topology file. This will enable proper handling of network interfaces after a reboot.
* Point to Multipoint connections are not supported at this time.
* Vagrantfiles written for the libvirt provider will come up in parallel by default regardless of the order specified in the Vagrantfile this give libvirt an obvious advantage for simulations with many nodes. To avoid this use "vagrant up --provider=libvirt --no-parallel
* The Virtualbox provider supports a maximum of 36 interfaces of which one is consumed by the vagrant interface giving an end-user 35 interfaces to interconnect in the topology. (I am not aware of any such interface limitation on libvirt)
* **Note that topology converter requires that python be installed on whatever system is to be simulated so that interface remapping can be performed via the apply_udev.py script.** This is especially important for devices running Fedora (which does not ship with python installed by default)



# Example Topologies
These topologies can be used to get started with topology converter.

## The Reference Topology
This topology can be used to simulate any feature offered by Cumulus Linux. It is not necessary to turn on each device in this topology, only those which you intend to use (to keep the simulation more manageable on a laptop). For more information on the reference topology see the [internal wiki page](https://wiki.cumulusnetworks.com/display/SAL/Reference+Topology), public documentation on the Reference Topology is coming soon!

![Reference Topology](reference_topology.png)

## 2 Switch Topology
Simple 2 Switch connectivity at it's best. 4 links of fury.


![2 Switch Topology](2switch.png)

## 1 Switch 1 Server Topology
Great to test Quagga on the Host Scenarios.


![1 Switch 1 Server Topology](1switch_1server.png)

## 2 Switch 1 Server Topology
Your basic MLAG scenario.


![2 Switch 1 Server Topology](2switch_1server.png)

## 3 Switch Circular Topology
This topology can be linear if you shut one of the links somewhere in the topology. Useful for testing the propogation of routing updates and configurations.


![3 Switch Circular Topology](3switch_circular.png)

