# Topology Converter
=====================

## See the [Documentation Section](./documentation) for way more information!!!



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

## What is it?
Topology Converter can help you to simulate a custom network topology built of Cumulus VX devices and any other linux-based devices you so choose.
Topology Converter uses a graphviz topology file to represent the entire topology. Topology Converter will convert this topology file into a Vagrantfile which fully represents the topology. Vagrantfiles are used with the popular simulation tool Vagrant to interconnect VMs. The topology can then be simulated in either Virtualbox or Libvirt (/w KVM) using Vagrant.


## Quick Examples: 
Run topology_converter against a topology file: 

```
    $ python ./topology_converter.py ./examples/2switch.dot
```


To see all the possible options use the help syntax "-h"

```
    $ python ./topology_converter.py -h
```

# Coming in v4.2.0
* Version Argument for TC
* Support for Ubuntu1604 Images (Done)
  * There is an issue with mutating boxes for libvirt (Under Investigation)



## Changelog:

* v4\.2\.0 TBD: 
* v4\.1\.0 2016\_05\_25: Added Support for VX 3.0, Added support for Version as a node Attribute, added support for pxebooting in virtualbox, added determinisic interface ordering in Vagrantfiles. Added Support for prepending "left_" and "right_" to any passthrough link attribute to specify which side of the link the attribute applies to. Added more realistic licensing support and switchd behavior in 2.5.x branches.
* v4\.0\.5 2016\_05\_05: Fixed UDEV Remap to tie rules to interfaces on the PCI Bus. Fixed Fake Device support. Added check to confirm that future Vagrant interfaces are tied to the PCI bus.
* v4\.0\.4 2016\_05\_01: Added functional defaults and check for node/device existance when parsing edges/links.
* v4\.0\.3 2016\_04\_25: Added link-based passthrough attribute support, disabled zipfile generation-- needs more work, removed use_vagrant_interface_option
* v4\.0\.2 2016\_04\_14: Added UDEV Based Remapping
* v4\.0\.1 2016\_04\_14: Added Extensible Template Handling, Print Arg Support, node-based passthrough attributes
* v4\.0\.0 2016\_04\_11: MAJOR UPDATES... moved to jinja2 templates, pygraphviz library and removal of the definitions file, added multi-device tunnel support via libvirt.
* v3\.4\.4 2016\_03\_31: Added support for MAC handout on any interface, not just a specified MGMT interface.
* v3\.4\.3 2016\_03\_22: Added libvirt interface name support.
* v3\.4\.2 2016\_03\_21: Adding Exception catching for lack of cumulus-vagrant plugin
* v3\.4\.1 2016\_03\_16: Use Seconds from EPOCH as an extenstion to the device name in Vbox.
* v3\.4 2016\_03\_15 Use Seconds from EPOCH as an extenstion to the unique net number to add some limited network isolation for the vbox use case. Also fixed zipfile generation to include all needed files.
* v3\.3 2016\_03\_09 All Hosts are now remapped by default. Removed Debian_Host_Remaps as a required setting. Added simple true/false check for if the host is Ubuntu. moved "use_vagrant_interface" option into the definitions file; this option creates and uses Vagrant interface instead of the Default 1st interface (usually eth0)
* v3\.2 2016\_03\_08 Significant changes to surrounding packages i.e. rename_eth_swp script. Minor changes to topology converter in the way remap files are generated and hosts run the remap at reboot via rc.local.
* v3\.1 2016\_03\_03 Added Hidden "use_vagrant_interface" option to optionally use Vagrant interface. Added CLI for Debugging mode.
* v3\.0 2016\_02\_23 Added support for Interface Remapping without reboots on Vx and Hosts (to save time). Moved any remaining topology-specific settings into the definitions files. So topology_converter is truly agnostic and should not need to be modified. Also created an option to disable the vagrant synced folder to further speed boot. Hardened Interface remapping on hosts to work on reboots; and not to pause and wait for networking at reboot. Created remap_eth_swp script that is both hardened and works for both Vx nodes and generic hosts.
* v2\.8 2016\_02\_05 Added support for .def files along with definitions.py so seperate files can be stored in the same directory. Also added support for adding topology files to shareable zipfile.
* v2\.7 2016\_01\_27 Setup cleanup of remap_files added zip file for generated files
* v2\.6 2016\_01\_26 Moved provider and switch/server mem settings from topology_converter to definitions.py
* v2\.5 2016\_01\_25 Added libvirt support :) and added support for fake devices!
* v2\.2 2016\_01\_19 Added Support for optional switch interface configuration
* v2\.1 2016\_01\_15 Added Support Boot Ordering -- 1st device --> 2nd device --> servers --> switches
* v2\.0 2016\_01\_07 Added Support for MAC handout, empty ansible playbook (used to generate ansible inventory), [EMPTY] connections for more accurate automation simulation, 
"vagrant" interface remapping for hosts and switches, warnings for interface reuse, added optional support for OOB switch.
* v1\.0 2015\_10\_19 Initial version constructed


