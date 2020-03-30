#!/usr/bin/env python3

#
#    Topology Converter
#       converts a given topology.dot file to a Vagrantfile
#           can use the virtualbox or libvirt Vagrant providers
# Initially written by Eric Pulvino 2015-10-19
#
#  hosted @ https://github.com/cumulusnetworks/topology_converter
#
#
version = "4.7.1"


import os
import re
import time
import pprint
import jinja2
import argparse
import importlib
import ipaddress
from operator import itemgetter

from lib.tc_config import TcConfig
from lib.warning_messages import WarningMessages
from lib.parse_topology import parse_topology
from lib.tc_error import TcError
from lib.styles import styles

pp = pprint.PrettyPrinter(depth=6)

parser = argparse.ArgumentParser(description='Topology Converter -- Convert \
                                 topology.dot files into Vagrantfiles')
parser.add_argument('topology_file',
                    help='provide a topology file as input')
parser.add_argument('-v', '--verbose', action='count', default=0,
                    help='increases logging verbosity (repeat for more verbosity (3 max))')
parser.add_argument('-p', '--provider', choices=["libvirt", "virtualbox"],
                    help='specifies the provider to be used in the Vagrantfile, \
                    script supports "virtualbox" or "libvirt", default is virtualbox.')
parser.add_argument('-a', '--ansible-hostfile', action='store_true',
                    help='When specified, ansible hostfile will be generated \
                    from a dummy playbook run.')
parser.add_argument('-c', '--create-mgmt-network', action='store_true',
                    help='When specified, a mgmt switch and server will be created. \
                    A /24 is assumed for the mgmt network. mgmt_ip=X.X.X.X will be \
                    read from each device to create a Static DHCP mapping for \
                    the oob-mgmt-server.')
parser.add_argument('-cco', '--create-mgmt-configs-only', action='store_true',
                    help='Calling this option does NOT regenerate the Vagrantfile \
                    but it DOES regenerate the configuration files that come \
                    packaged with the mgmt-server in the "-c" option. This option \
                    is typically used after the "-c" has been called to generate \
                    a Vagrantfile with an oob-mgmt-server and oob-mgmt-switch to \
                    modify the configuraiton files placed on the oob-mgmt-server \
                    device. Useful when you do not want to regenerate the \
                    vagrantfile but you do want to make changes to the \
                    OOB-mgmt-server configuration templates.')
parser.add_argument('-cmd', '--create-mgmt-device', action='store_true',
                    help='Calling this option creates the mgmt device and runs the \
                    auto_mgmt_network template engine to load configurations on to \
                    the mgmt device but it does not create the OOB-MGMT-SWITCH or \
                    associated connections. Useful when you are manually specifying \
                    the construction of the management network but still want to have \
                    the OOB-mgmt-server created automatically.')
parser.add_argument('-t', '--template', action='append', nargs=2,
                    help='Specify an additional jinja2 template and a destination \
                    for that file to be rendered to.')
parser.add_argument('-i', '--tunnel-ip',
                    help='FOR LIBVIRT PROVIDER: this option overrides the tunnel_ip \
                    setting for all nodes. This option provides another method of \
                    udp port control in that all ports are bound to the specified \
                    ip address. Specify "random" to use a random localhost IP.')
parser.add_argument('-s', '--start-port', type=int,
                    help='FOR LIBVIRT PROVIDER: this option overrides \
                    the default starting-port 8000 with a new value. \
                    Use ports over 1024 to avoid permissions issues. If using \
                    this option with the virtualbox provider it will be ignored.')
parser.add_argument('-g', '--port-gap', type=int,
                    help='FOR LIBVIRT PROVIDER: this option overrides the \
                    default port-gap of 1000 with a new value. This number \
                    is added to the start-port value to determine the port \
                    to be used by the remote-side. Port-gap also defines the \
                    max number of links that can exist in the topology. EX. \
                    If start-port is 8000 and port-gap is 1000 the first link \
                    will use ports 8001 and 9001 for the construction of the \
                    UDP tunnel. If using this option with the virtualbox \
                    provider it will be ignored.')
parser.add_argument('-dd', '--display-datastructures', action='store_true',
                    help='When specified, the datastructures which are passed \
                    to the template are displayed to screen. Note: Using \
                    this option does not write a Vagrantfile and \
                    supercedes other options.')
parser.add_argument('--synced-folder', action='store_true',
                    help='Using this option enables the default Vagrant \
                    synced folder which we disable by default. \
                    See: https://www.vagrantup.com/docs/synced-folders/basic_usage.html')
parser.add_argument('--version', action='version', version="Topology \
                    Converter version is v%s" % version,
                    help='Using this option displays the version of Topology Converter')
parser.add_argument('--prefix', help='Specify a prefix to be used for machines in libvirt. By default the name of the current folder is used.')
args = parser.parse_args()

# Dynamic Variables
relpath_to_me = os.path.relpath(os.path.dirname(os.path.abspath(__file__)), os.getcwd())

# Determine whether local or global templates will be used.
template_storage = None
VAGRANTFILE = 'Vagrantfile'
if os.path.isdir('./templates'):
    template_storage = './templates'
else:
    template_storage = relpath_to_me + '/templates'
VAGRANTFILE_template = template_storage + "/Vagrantfile.j2"
TEMPLATES = [[VAGRANTFILE_template, VAGRANTFILE]]

# Parse Arguments
TC_CONFIG = TcConfig(**args.__dict__)
TC_CONFIG.parser = parser
network_functions = TC_CONFIG.network_functions
function_group = TC_CONFIG.function_group
provider = TC_CONFIG.provider
generate_ansible_hostfile = TC_CONFIG.generate_ansible_hostfile
create_mgmt_device = TC_CONFIG.create_mgmt_device
create_mgmt_network = TC_CONFIG.create_mgmt_network
create_mgmt_configs_only = TC_CONFIG.create_mgmt_configs_only
verbose = TC_CONFIG.verbose
tunnel_ip = TC_CONFIG.tunnel_ip
start_port = TC_CONFIG.start_port
port_gap = TC_CONFIG.port_gap
synced_folder = TC_CONFIG.synced_folder
display_datastructures = TC_CONFIG.display_datastructures
arg_string = TC_CONFIG.arg_string
libvirt_prefix = TC_CONFIG.libvirt_prefix
customer = TC_CONFIG.customer
vagrant = TC_CONFIG.vagrant

# Determine whether local or global helper_scripts will be used.
if os.path.isdir('./helper_scripts'):
    TC_CONFIG.script_storage = './helper_scripts'
else:
    TC_CONFIG.script_storage = relpath_to_me+"/helper_scripts"
script_storage = TC_CONFIG.script_storage

if args.topology_file: topology_file = args.topology_file

if args.verbose: verbose = args.verbose

if args.provider: provider = args.provider

if args.ansible_hostfile: generate_ansible_hostfile = True

if args.create_mgmt_device:
    create_mgmt_device = True
    vagrant = "vagrant"

if args.create_mgmt_network:
    create_mgmt_device = True
    create_mgmt_network = True
    vagrant = "vagrant"

if args.create_mgmt_configs_only:
    create_mgmt_configs_only = True
    vagrant = "vagrant"

if args.template:
    for templatefile, destination in args.template:
        TEMPLATES.append([templatefile, destination])

for templatefile, destination in TEMPLATES:
    if not os.path.isfile(templatefile):
        print(styles.FAIL + styles.BOLD + " ### ERROR: provided template file-- \"" +
              templatefile + "\" does not exist!" + styles.ENDC)
        exit(1)

if args.tunnel_ip:
    if provider == 'libvirt':
        tunnel_ip = args.tunnel_ip
        if tunnel_ip != 'random':
            try:
                ipaddress.ip_address(tunnel_ip)
            except ValueError as e:
                print(styles.FAIL + styles.BOLD + " ### ERROR: " + str(e) + "."
                      + " Specify 'random' to use a random localhost IPv4 address."
                      + styles.ENDC)
                exit(1)
    else:
        print(styles.FAIL + styles.BOLD + " ### ERROR: tunnel IP was specified but " +
              "provider is not libvirt." + styles.ENDC)
        exit(1)

if args.start_port: start_port = args.start_port

if args.port_gap: port_gap = args.port_gap

if args.display_datastructures: display_datastructures = True

if args.synced_folder: synced_folder = True

if args.prefix != None: libvirt_prefix = args.prefix

# Use Prefix as customer name if available
if libvirt_prefix:
    customer = libvirt_prefix
else:
    customer = os.path.basename(os.path.dirname(os.getcwd()))

if verbose > 2:
    print("Arguments:")
    print(args)

if verbose > 2:
    print("relpath_to_me: {}".format(relpath_to_me))

###################################
#### MAC Address Configuration ####
###################################

# The starting MAC for assignment for any devices not in mac_map
# Cumulus Range ( https://support.cumulusnetworks.com/hc/en-us/articles/203837076-Reserved-MAC-Address-Range-for-Use-with-Cumulus-Linux )
TC_CONFIG.start_mac = "443839000000"

# This file is generated to store the mapping between macs and interfaces
dhcp_mac_file = "./dhcp_mac_map"

######################################################
#############    Everything Else     #################
######################################################

# Hardcoded Variables
epoch_time = str(int(time.time()))
mac_map = TC_CONFIG.mac_map
warning = WarningMessages()

# Static Variables -- Do not change!
libvirt_reuse_error = """
       When constructing a VAGRANTFILE for the libvirt provider
       interface reuse is not possible because the UDP tunnels
       which libvirt uses for communication are point-to-point in
       nature. It is not possible to create a point-to-multipoint
       UDP tunnel!

       NOTE: Perhaps adding another switch to your topology would
       allow you to avoid reusing interfaces here.
"""

###### Functions
def clean_datastructure(devices):
    global verbose

    # Sort the devices by function
    devices.sort(key=getKeyDevices)
    for device in devices:
        device['interfaces'] = sorted_interfaces(device['interfaces'])

    if display_datastructures:
        return devices
    for device in devices:
        if verbose > 0:
            print(styles.GREEN + styles.BOLD + ">> DEVICE: " + device['hostname'] + styles.ENDC)
            print("     code: " + device['os'])

            if 'memory' in device:
                print("     memory: " + device['memory'])

            for attribute in device:
                if attribute == 'memory' or attribute == 'os' or attribute == 'interfaces':
                    continue
                print("     " + str(attribute) + ": " + str(device[attribute]))

        if verbose > 1:
            for interface_entry in device['interfaces']:
                print("       LINK: " + interface_entry["local_interface"])
                for attribute in interface_entry:
                    if attribute != "local_interface":
                        print("               " + attribute + ": " + interface_entry[attribute])

    # Remove Fake Devices
    indexes_to_remove = []
    for i in range(0, len(devices)):
        if 'function' in devices[i]:
            if devices[i]['function'] == 'fake':
                indexes_to_remove.append(i)
    for index in sorted(indexes_to_remove, reverse=True):
        del devices[index]
    return devices


def remove_generated_files():
    if display_datastructures:
        return
    if verbose > 2:
        print("Removing existing DHCP FILE...")
    if os.path.isfile(dhcp_mac_file):
        os.remove(dhcp_mac_file)


def natural_sort_key(s):
    _nsre = re.compile('([0-9]+)')
    if s == 'eth0': return ['A',0,'']
    return [int(text) if text.isdigit() else text.lower()
            for text in re.split(_nsre, s)]


def getKeyDevices(device):
    # Used to order the devices for printing into the vagrantfile
    if device['function'] == "oob-server":
        return 1
    elif device['function'] == "oob-switch":
        return 2
    elif device['function'] == "exit":
        return 3
    elif device['function'] == "superspine":
        return 4
    elif device['function'] == "spine":
        return 5
    elif device['function'] == "leaf":
        return 6
    elif device['function'] == "tor":
        return 7
    elif device['function'] == "host":
        return 8
    else:
        return 9


def sorted_interfaces(interface_dictionary):
    sorted_list = []
    interface_list = []

    for link in interface_dictionary:
        sorted_list.append(link)

    sorted_list.sort(key=natural_sort_key)

    for link in sorted_list:
        interface_dictionary[link]["local_interface"] = link
        interface_list.append(interface_dictionary[link])

    return interface_list


def generate_dhcp_mac_file(mac_map):
    if verbose > 2:
        print("GENERATING DHCP MAC FILE...")

    mac_file = open(dhcp_mac_file, "a")

    if '' in mac_map:
        del mac_map['']

    dhcp_display_list = []

    for line in mac_map:
        dhcp_display_list.append(mac_map[line] + "," + line)

    dhcp_display_list.sort()

    for line in dhcp_display_list:
        mac_file.write(line + "\n")

    mac_file.close()


def populate_data_structures(inventory):
    global function_group
    devices = []

    for device in inventory:
        inventory[device]['hostname'] = device
        devices.append(inventory[device])

    devices_clean = clean_datastructure(devices)

    # Create Functional Group Map
    for device in devices_clean:

        if device['function'] not in function_group:
            function_group[device['function']] = []

        function_group[device['function']].append(device['hostname'])

    return devices_clean


def render_jinja_templates(devices):
    global function_group

    if display_datastructures:
        print_datastructures(devices)

    if verbose > 2:
        print("RENDERING JINJA TEMPLATES...")

    # Render the MGMT Network stuff
    mgmt_destination_dir = "./helper_scripts/auto_mgmt_network/"
    if create_mgmt_device:
        # Check that MGMT Template Dir exists
        mgmt_template_dir = template_storage + "/auto_mgmt_network/"
        if not os.path.isdir(mgmt_template_dir):
            print(styles.FAIL + styles.BOLD +
                  "ERROR: " + mgmt_template_dir +
                  " does not exist. Cannot populate templates!" +
                  styles.ENDC)

            exit(1)

        # Scan MGMT Template Dir for .j2 files
        mgmt_templates = []

        for file in os.listdir(mgmt_template_dir):

            if file.endswith(".j2"):
                mgmt_templates.append(file)

        if verbose > 2:
            print(" mgmt_template_dir: {}".format(mgmt_template_dir))
            print(" detected mgmt_templates:")
            print(mgmt_templates)

        # Create output location for MGMT template files
        if not os.path.isdir(mgmt_destination_dir):
            if verbose > 2:
                print("Making Directory for MGMT Helper Files: " + mgmt_destination_dir)

            try:
                os.makedirs(mgmt_destination_dir)

            except:
                print(styles.FAIL + styles.BOLD +
                      "ERROR: Could not create output directory for mgmt template renders!" +
                      styles.ENDC)
                exit(1)

        # Render out the templates
        for template in mgmt_templates:
            render_destination = os.path.join(mgmt_destination_dir, template[0:-3])
            template_source = os.path.join(mgmt_template_dir, template)
            TEMPLATES.append([template_source,render_destination])

    # If just rendering mgmt templates, remove Vagrantfile from list
    if create_mgmt_device and create_mgmt_configs_only:
        del TEMPLATES[0]

    # Render the Templates
    for templatefile, destination in TEMPLATES:

        if verbose > 2:
            print("    Rendering: " + templatefile + " --> " + destination)

        template = jinja2.Template(open(templatefile).read())

        with open(destination, 'w') as outfile:
            outfile.write(template.render(devices=devices,
                                          start_port=start_port,
                                          port_gap=port_gap,
                                          synced_folder=synced_folder,
                                          provider=provider,
                                          version=version,
                                          customer=customer,
                                          topology_file=topology_file,
                                          arg_string=arg_string,
                                          epoch_time=epoch_time,
                                          mgmt_destination_dir=mgmt_destination_dir,
                                          generate_ansible_hostfile=generate_ansible_hostfile,
                                          create_mgmt_device=create_mgmt_device,
                                          function_group=function_group,
                                          network_functions=network_functions,
                                          libvirt_prefix=libvirt_prefix,))


def print_datastructures(devices):
    print("\n\n######################################")
    print("   DATASTRUCTURES SENT TO TEMPLATE:")
    print("######################################\n")
    print("provider=" + provider)
    print("synced_folder=" + str(synced_folder))
    print("version=" + str(version))
    print("topology_file=" + topology_file)
    print("arg_string=" + arg_string)
    print("epoch_time=" + str(epoch_time))
    print("script_storage=" + script_storage)
    print("generate_ansible_hostfile=" + str(generate_ansible_hostfile))
    print("create_mgmt_device=" + str(create_mgmt_device))
    print("function_group=")
    pp.pprint(function_group)
    print("network_functions=")
    pp.pprint(network_functions)
    print("devices=")
    pp.pprint(devices)
    exit(0)


def generate_ansible_files():
    if not generate_ansible_hostfile:
        return

    if verbose > 2:
        print("Generating Ansible Files...")

    with open(script_storage+"/empty_playbook.yml", "w") as playbook:
        playbook.write("""---
- hosts: all
  user: vagrant
  gather_facts: no
  tasks:
    - command: "uname -a"
""")

    with open("./ansible.cfg", "w") as ansible_cfg:
        ansible_cfg.write("""[defaults]
inventory = ./.vagrant/provisioners/ansible/inventory/vagrant_ansible_inventory
hostfile= ./.vagrant/provisioners/ansible/inventory/vagrant_ansible_inventory
host_key_checking=False
callback_whitelist = profile_tasks
jinja2_extensions=jinja2.ext.do""")


def main():
    global mac_map
    print(styles.HEADER + "\n######################################")
    print(styles.HEADER + "          Topology Converter")
    print(styles.HEADER + "######################################")
    print(styles.BLUE + "           originally written by Eric Pulvino")

    try:
        inventory = parse_topology(topology_file, TC_CONFIG)
    except TcError:
        exit(1)

    devices = populate_data_structures(inventory)

    remove_generated_files()

    render_jinja_templates(devices)

    generate_dhcp_mac_file(mac_map)

    generate_ansible_files()

    if create_mgmt_configs_only:
        print(styles.GREEN + styles.BOLD +
              "\n############\nSUCCESS: MGMT Network Templates have been regenerated!\n############" +
              styles.ENDC)
    else:
        print(styles.GREEN + styles.BOLD +
              "\n############\nSUCCESS: Vagrantfile has been generated!\n############" +
              styles.ENDC)
        print(styles.GREEN + styles.BOLD +
              "\n            %s devices under simulation." % (len(devices)) +
              styles.ENDC)

        for device in inventory:
            print(styles.GREEN + styles.BOLD +
                  "                %s" % (inventory[device]['hostname']) +
                  styles.ENDC)
        print(styles.GREEN + styles.BOLD +
              "\n            Requiring at least %s MBs of memory." % (TC_CONFIG.total_memory) +
              styles.ENDC)


    warning.print_warnings()

    print("\nDONE!\n")


if __name__ == "__main__":
    main()

exit(0)
