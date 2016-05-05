#!/usr/bin/env python

#
#    Topology Converter
#       converts a given topology.dot file to a Vagrantfile
#           can use the virtualbox or libvirt Vagrant providers
# Initially written by Eric Pulvino 2015-10-19
#
#  hosted @ https://github.com/cumulusnetworks/topology_converter
#
#
version = "4.0.5"


import os
import re
import sys
import time
import pprint
import jinja2
import argparse
import importlib
import pydotplus

pp = pprint.PrettyPrinter(depth=6)


parser = argparse.ArgumentParser(description='Topology Converter -- Convert topology.dot files into Vagrantfiles')
parser.add_argument('topology_file',
                   help='provide a topology file as input')
parser.add_argument('-v','--verbose', action='store_true',
                   help='enables verbose logging mode')
parser.add_argument('-p','--provider', choices=["libvirt","virtualbox"],
                   help='specifies the provider to be used in the Vagrantfile, script supports "virtualbox" or "libvirt", default is virtualbox.')
parser.add_argument('-a','--ansible-hostfile', action='store_true',
                   help='When specified, ansible hostfile will be generated from a dummy playbook run.')
parser.add_argument('-t','--template', action='append', nargs=2,
                   help='Specify an additional jinja2 template and a destination for that file to be rendered to.')
parser.add_argument('-s','--start-port', type=int,
                   help='FOR LIBVIRT PROVIDER: this option overrides the default starting-port 8000 with a new value. Use ports over 1024 to avoid permissions issues. If using this option with the virtualbox provider it will be ignored.')
parser.add_argument('-g','--port-gap', type=int,
                   help='FOR LIBVIRT PROVIDER: this option overrides the default port-gap of 1000 with a new value. This number is added to the start-port value to determine the port to be used by the remote-side. Port-gap also defines the max number of links that can exist in the topology. EX. If start-port is 8000 and port-gap is 1000 the first link will use ports 8001 and 9001 for the construction of the UDP tunnel. If using this option with the virtualbox provider it will be ignored.')
parser.add_argument('-dd','--display-datastructures', action='store_true',
                   help='When specified, the datastructures which are passed to the template are displayed to screen. Note: Using this option does not write a Vagrantfile and supercedes other options.')
parser.add_argument('--synced-folder', action='store_true',
                   help='Using this option enables the default Vagrant synced folder which we disable by default. See: https://www.vagrantup.com/docs/synced-folders/basic_usage.html')
args = parser.parse_args()

#Parse Arguments
provider="virtualbox"
generate_ansible_hostfile=False
verbose=False
start_port=8000
port_gap=1000
synced_folder=False
display_datastructures=False
VAGRANTFILE='Vagrantfile'
VAGRANTFILE_template='templates/Vagrantfile.j2'
TEMPLATES=[[VAGRANTFILE_template,VAGRANTFILE]]
if args.topology_file: topology_file=args.topology_file
if args.verbose: verbose=args.verbose
if args.provider: provider=args.provider
if args.ansible_hostfile: generate_ansible_hostfile=True
if args.template:
    for templatefile,destination in args.template:
        TEMPLATES.append([templatefile,destination])
for templatefile,destination in TEMPLATES:
    if not os.path.isfile(templatefile):
        print " ### ERROR: provided template file-- \"" + templatefile + "\" does not exist!"
        exit(1)
if args.start_port: start_port=args.start_port
if args.port_gap: port_gap=args.port_gap
if args.display_datastructures: display_datastructures=True
if args.synced_folder: synced_folder=True

if verbose:
    print "Arguments:"
    print args

###################################
#### MAC Address Configuration ####
###################################

# The starting MAC for assignment for any devices not in mac_map
#Cumulus Range ( https://support.cumulusnetworks.com/hc/en-us/articles/203837076-Reserved-MAC-Address-Range-for-Use-with-Cumulus-Linux )
start_mac="443839000000"
#This file is generated to store the mapping between macs and mgmt interfaces
dhcp_mac_file="./dhcp_mac_map"

######################################################
#############    Everything Else     #################
######################################################

# By default, Vagrant will share the directory with the Vagrantfile to /vagrant on the host
#  use this knob to enable or disable that ability.
synced_folder=False

#Hardcoded Variables
script_storage="./helper_scripts" #Location for our generated remap files
ZIPFILE="./virtual_topology.zip"
epoch_time = str(int(time.time()))
mac_map={}

#LIBvirt Provider Settings
# start_port and port_gap are only relevant to the libvirt provider. These settings provide the basis
#   for the UDP tunnel construction which is used by libvirt. Since UDP tunnels only make sense in a 
#   point-to-point fashion, there is additional error checking when using the libvirt provider to make
#   sure that interfaces are not reused for a point-to-multipoint configuration.


#Static Variables -- #Do not change!
warning=False
libvirt_reuse_error="""
       When constructing a VAGRANTFILE for the libvirt provider
       interface reuse is not possible because the UDP tunnels
       which libvirt uses for communication are point-to-point in
       nature. It is not possible to create a point-to-multipoint
       UDP tunnel!

       NOTE: Perhaps adding another switch to your topology would
       allow you to avoid reusing interfaces here.
"""

###### Functions
def mac_fetch(hostname,interface):
    global start_mac
    global mac_map
    global warning
    new_mac = hex(int(start_mac, 16) + 1)[2:].upper()
    while new_mac in mac_map:
        print " WARNING: MF MAC Address Collision -- tried to use " + new_mac + " (on "+interface+") but it was already in use."
        start_mac = new_mac
        new_mac = hex(int(start_mac, 16) + 1)[2:].upper()
        warning=True
    start_mac = new_mac
    return str(new_mac)

def parse_topology(topology_file):
    global provider
    global verbose
    global warning
    topology = pydotplus.graphviz.graph_from_dot_file(topology_file)
    inventory = {}
    nodes=topology.get_node_list()
    edges=topology.get_edge_list()
    for node in nodes:
        node_name=node.get_name().replace('"','')
        #Add node to inventory
        if node_name not in inventory:
            inventory[node_name] = {}
            inventory[node_name]['interfaces'] = {}

        node_attr_list=node.get_attributes()
        print "node_attr_list:"
        print node_attr_list

        #Define Functional Defaults
        if 'function' in node_attr_list:
            value=node.get('function')
            if value.startswith('"') or value.startswith("'"): value=value[1:].lower()
            if value.endswith('"') or value.endswith("'"): value=value[:-1].lower()

            if value=='fake':
                inventory[node_name]['os']="None"
                inventory[node_name]['memory']="1"
            if value=='oob-server':
                inventory[node_name]['os']="boxcutter/ubuntu1604"
                inventory[node_name]['memory']="500"
            elif value=='oob-switch':
                inventory[node_name]['os']="CumulusCommunity/cumulus-vx"
                inventory[node_name]['memory']="300"
            elif value=='exit':
                inventory[node_name]['os']="CumulusCommunity/cumulus-vx"
                inventory[node_name]['memory']="300"
            elif value=='spine':
                inventory[node_name]['os']="CumulusCommunity/cumulus-vx"
                inventory[node_name]['memory']="300"
            elif value=='leaf':
                inventory[node_name]['os']="CumulusCommunity/cumulus-vx"
                inventory[node_name]['memory']="300"
            elif value=='host':
                inventory[node_name]['os']="boxcutter/ubuntu1604"
                inventory[node_name]['memory']="500"

        #Add attributes to node inventory
        for attribute in node_attr_list:
            #if verbose: print attribute + " = " + node.get(attribute)
            value=node.get(attribute)
            if value.startswith('"') or value.startswith("'"): value=value[1:]
            if value.endswith('"') or value.endswith("'"): value=value[:-1]
            inventory[node_name][attribute] = value

        #Make sure mandatory attributes are present.
        mandatory_attributes=['os',]
        for attribute in mandatory_attributes:
            if attribute not in inventory[node_name]:
                print " ### ERROR: MANDATORY DEVICE ATTRIBUTE \""+attribute+"\" not specified for "+ node_name
                exit(1)

        #Extra Massaging for specific attributes.
        #   light sanity checking.
        if 'function' not in inventory[node_name]: inventory[node_name]['function'] = "Unknown"
        if 'memory' in inventory[node_name]:
            if int(inventory[node_name]['memory']) <= 0:
                print " ### ERROR -- Memory must be greater than 0mb on " + node_name
                exit(1)
        if provider == "libvirt":
            if 'tunnel_ip' not in inventory[node_name]: inventory[node_name]['tunnel_ip']='127.0.0.1'


    net_number = 1
    for edge in edges:
        if provider=="virtualbox":
            network_string="net"+str(net_number)

        elif provider=="libvirt":
            PortA=str(start_port+net_number)
            PortB=str(start_port+port_gap+net_number)
            if int(PortA) > int(start_port+port_gap):
                print " ### ERROR: Configured Port_Gap: ("+str(port_gap)+") exceeds the number of links in the topology. Read the help options to fix.\n\n"
                parser.print_help()
                exit(1)

        #Handle Link-based Passthrough Attributes
        edge_attributes={}
        for attribute in edge.get_attributes():
            if attribute=="left_mac" or attribute=="right_mac": continue
            if attribute in edge_attributes:
                print " ### WARNING: Attribute \""+attribute+"\" specified twice. Using second value."
                warning=True
            value=edge.get(attribute)
            if value.startswith('"') or value.startswith("'"): value=value[1:]
            if value.endswith('"') or value.endswith("'"): value=value[:-1]
            edge_attributes[attribute]=value

        #Set Devices/interfaces/MAC Addresses
        left_device=edge.get_source().split(":")[0].replace('"','')
        left_interface=edge.get_source().split(":")[1].replace('"','')
        right_device=edge.get_destination().split(":")[0].replace('"','')
        right_interface=edge.get_destination().split(":")[1].replace('"','')

        left_mac_address=""
        if edge.get('left_mac') != None : left_mac_address=edge.get('left_mac').replace('"','')
        else: left_mac_address=mac_fetch(left_device,left_interface)
        right_mac_address=""
        if edge.get('right_mac') != None : right_mac_address=edge.get('right_mac').replace('"','')
        else: right_mac_address=mac_fetch(right_device,right_interface)

        #Check to make sure each device in the edge already exists in inventory
        if left_device not in inventory:
            print " ### ERROR: device " + left_device + " is referred to in list of edges/links but not defined as a node."
            exit(1)
        if right_device not in inventory:
            print " ### ERROR: device " + right_device + " is referred to in list of edges/links but not defined as a node."
            exit(1)

        #Add left host switchport to inventory
        if left_interface not in inventory[left_device]['interfaces']:
            inventory[left_device]['interfaces'][left_interface] = {}
            inventory[left_device]['interfaces'][left_interface]['mac']=left_mac_address
            if left_mac_address in mac_map:
                print " ### ERROR -- MAC Address Collision - tried to use "+left_mac_address+" on "+left_device+":"+left_interface+"\n                 but it is already in use. Check your Topology File!"
                exit(1)
            mac_map[left_mac_address]=left_device+","+left_interface
            if provider=="virtualbox":
                inventory[left_device]['interfaces'][left_interface]['network'] = network_string
            elif provider=="libvirt":
                inventory[left_device]['interfaces'][left_interface]['local_port'] = PortA
                inventory[left_device]['interfaces'][left_interface]['remote_port'] = PortB
        else:
            print " ### ERROR -- Interface " + left_interface + " Already used on device: " + left_device
            exit(1)

        #Add right host switchport to inventory
        if right_interface not in inventory[right_device]['interfaces']:
            inventory[right_device]['interfaces'][right_interface] = {}
            inventory[right_device]['interfaces'][right_interface]['mac']=right_mac_address
            if right_mac_address in mac_map:
                print " ### ERROR -- MAC Address Collision - tried to use "+right_mac_address+" on "+right_device+":"+right_interface+"\n                 but it is already in use. Check your Topology File!"
                exit(1)
            mac_map[right_mac_address]=right_device+","+right_interface
            if provider=="virtualbox":
                inventory[right_device]['interfaces'][right_interface]['network'] = network_string
            elif provider=="libvirt":
                inventory[right_device]['interfaces'][right_interface]['local_port'] = PortB
                inventory[right_device]['interfaces'][right_interface]['remote_port'] = PortA
        else:
            print " ### ERROR -- Interface " + right_interface + " Already used on device: " + right_device
            exit(1)

        inventory[left_device]['interfaces'][left_interface]['remote_interface'] = right_interface
        inventory[left_device]['interfaces'][left_interface]['remote_device'] = right_device

        inventory[right_device]['interfaces'][right_interface]['remote_interface'] = left_interface
        inventory[right_device]['interfaces'][right_interface]['remote_device'] = left_device
        if provider == 'libvirt':
            inventory[left_device]['interfaces'][left_interface]['local_ip'] = inventory[left_device]['tunnel_ip']
            inventory[left_device]['interfaces'][left_interface]['remote_ip'] = inventory[right_device]['tunnel_ip']
            inventory[right_device]['interfaces'][right_interface]['local_ip'] = inventory[right_device]['tunnel_ip']
            inventory[right_device]['interfaces'][right_interface]['remote_ip'] = inventory[left_device]['tunnel_ip']

        #Add link-based passthrough attributes
        for attribute in edge_attributes:
            inventory[left_device]['interfaces'][left_interface][attribute]=edge_attributes[attribute]
            inventory[right_device]['interfaces'][right_interface][attribute]=edge_attributes[attribute]
        net_number += 1

    if verbose:
        print "\n\n ### Inventory Datastructure: ###"
        pp.pprint(inventory)

    return inventory

def clean_datastructure(devices):
    #Sort the devices by function
    devices.sort(key=getKeyDevices)

    if display_datastructures: return devices
    for device in devices:
        print ">> DEVICE: " + device['hostname']
        print "     code: " + device['os']
        if 'memory' in device:
            print "     memory: " + device['memory']
        for attribute in device:
            if attribute == 'memory' or attribute == 'os' or attribute == 'interfaces': continue
            print "     "+str(attribute)+": "+ str(device[attribute])
        for interface in device['interfaces']:
            print "       LINK: " + interface
            for attribute in device['interfaces'][interface]:
                print "               " + attribute +": " + device['interfaces'][interface][attribute]

    #Remove Fake Devices
    indexes_to_remove=[]
    for i in range(0,len(devices)):
        if 'function' in devices[i]:
            if devices[i]['function'] == 'fake':
                indexes_to_remove.append(i)
    for index in indexes_to_remove: del devices[index]
    return devices

def remove_generated_files():
    if display_datastructures: return
    if verbose: print "Removing existing DHCP FILE..."
    if os.path.isfile(dhcp_mac_file):  os.remove(dhcp_mac_file)

def generate_shareable_zip():
    import zipfile
    topology_dir="./"+os.path.split(topology_file)[0]
    template_dir="./"+os.path.split(VAGRANTFILE_template)[0]
    topo_file=os.path.split(topology_file)[1]
    vagrantfile=os.path.split(VAGRANTFILE)[1]

    folders_to_zip=["./","./helper_scripts",]
    if topology_dir not in folders_to_zip: folders_to_zip.append(topology_dir)
    if template_dir not in folders_to_zip: folders_to_zip.append(template_dir)

    if verbose: print "Creating ZIP..."
    if verbose: print "  Folders_to_Zip: ["+", ".join(folders_to_zip)+"]"

    zf = zipfile.ZipFile(ZIPFILE, "w")
    for dirname, subdirs, files in os.walk("./"):
        if dirname in folders_to_zip:
            if verbose: print "  adding directory %s to zip..." % (dirname)
            zf.write(dirname)
            for filename in files:
                if filename.endswith("~") or filename.lower().endswith(".zip") or filename.startswith(".git"): continue
                elif dirname == topology_dir:
                    if filename != topo_file: continue
                file_to_add=os.path.join(dirname, filename)
                if verbose:
                    print "  adding %s to zip..." % (file_to_add)
                zf.write(file_to_add)
        else:
            continue
    zf.close()

def getKey(item):
    # Used to sort interfaces alphabetically
    base = 10
    if item[0:3].lower() == "eth": base = 0
    val = float(item[3:].replace("s","."))
    return val + base

def getKeyDevices(device):
    # Used to sort interfaces alphabetically

    if device['function'] == "oob-server": return 1
    elif device['function'] == "oob-switch": return 2
    elif device['function'] == "exit": return 3
    elif device['function'] == "spine": return 4
    elif device['function'] == "leaf": return 5
    elif device['function'] == "host": return 6
    else: return 7

def sorted_interfaces(interface_dictionary):
    interface_list=[]
    for link in interface_dictionary:
        interface_list.append(link)
    interface_list.sort(key=getKey)
    return interface_list

def generate_dhcp_mac_file(mac_map):
    if verbose: print "GENERATING DHCP MAC FILE..."
    mac_file = open(dhcp_mac_file,"a")
    if '' in mac_map: del mac_map['']
    dhcp_display_list=[]
    for line in mac_map:
        dhcp_display_list.append(mac_map[line]+","+line)
    dhcp_display_list.sort()
    for line in dhcp_display_list:
        mac_file.write(line+"\n")
    mac_file.close()

def populate_data_structures(inventory):
    devices = []
    for device in inventory:
        inventory[device]['hostname']=device
        devices.append(inventory[device])
    return clean_datastructure(devices)


def render_jinja_templates(devices):
    if display_datastructures: print_datastructures(devices)
    if verbose: print "RENDERING JINJA TEMPLATES..."
    for templatefile,destination in TEMPLATES:
        if verbose: print "    Rendering: " + templatefile + " --> " + destination
        template = jinja2.Template(open(templatefile).read())
        with open(destination, 'w') as outfile:
            outfile.write(template.render(devices=devices,
                                          synced_folder=synced_folder,
                                          provider=provider,
                                          version=version,
                                          topology_file=topology_file,
                                          epoch_time=epoch_time,
                                          script_storage=script_storage,
                                          generate_ansible_hostfile=generate_ansible_hostfile,)
                         )


def print_datastructures(devices):
    print "\n\n######################################"
    print "   DATASTRUCTURES SENT TO TEMPLATE:"
    print "######################################\n"
    print "provider=" + provider
    print "synced_folder=" + str(synced_folder)
    print "version=" + str(version)
    print "topology_file=" + topology_file
    print "epoch_time=" + str(epoch_time)
    print "script_storage=" + script_storage
    print "generate_ansible_hostfile=" + str(generate_ansible_hostfile)
    print "devices="
    pp.pprint(devices)
    exit(0)

def generate_ansible_files():
    if not generate_ansible_hostfile: return
    if verbose: print "Generating Ansible Files..."
    with open("./helper_scripts/empty_playbook.yml","w") as playbook:
        playbook.write("""---
- hosts: all
  user: vagrant
  gather_facts: no
  tasks:
    - command: "uname -a"
""")
    with open("./ansible.cfg","w") as ansible_cfg:
        ansible_cfg.write("""[defaults]
inventory = ./.vagrant/provisioners/ansible/inventory/vagrant_ansible_inventory
hostfile= ./.vagrant/provisioners/ansible/inventory/vagrant_ansible_inventory
host_key_checking=False
callback_whitelist = profile_tasks""")



def main():
    global mac_map
    print "\n######################################"
    print "          Topology Converter"
    print "######################################"

    inventory = parse_topology(topology_file)

    devices=populate_data_structures(inventory)

    remove_generated_files()

    render_jinja_templates(devices)

    generate_dhcp_mac_file(mac_map)

    generate_ansible_files()

    #generate_shareable_zip() #Disabled because it is unreliable


if __name__ == "__main__":
    main()
    print "\nVagrantfile has been generated!\n"
    print "\nDONE!\n"
exit(0)
