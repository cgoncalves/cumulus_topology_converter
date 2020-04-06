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
import argparse
import ipaddress

from topology_converter.tc_config import TcConfig
from topology_converter.tc_error import RenderError, TcError
from topology_converter.parse_topology import parse_topology
from topology_converter.renderer import Renderer
from topology_converter.styles import styles
from topology_converter.warning_messages import WarningMessages

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

# Parse Arguments
TC_CONFIG = TcConfig(**args.__dict__)
TC_CONFIG.parser = parser
TC_CONFIG.version = version
network_functions = TC_CONFIG.network_functions
function_group = TC_CONFIG.function_group
provider = TC_CONFIG.provider
generate_ansible_hostfile = TC_CONFIG.ansible_hostfile
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
libvirt_prefix = TC_CONFIG.prefix
vagrant = TC_CONFIG.vagrant

topology_file = TC_CONFIG.topology_file

# Determine whether local or global helper_scripts will be used.
if os.path.isdir('./helper_scripts'):
    TC_CONFIG.script_storage = './helper_scripts'
else:
    TC_CONFIG.script_storage = TC_CONFIG.relpath_to_me+"/helper_scripts"
script_storage = TC_CONFIG.script_storage

if create_mgmt_device or args.create_mgmt_configs_only:
    TC_CONFIG.vagrant = 'vagrant'

if create_mgmt_network:
    TC_CONFIG.vagrant = 'vagrant'
    TC_CONFIG.create_mgmt_device = True
    create_mgmt_device = True

if args.template:
    for templatefile, destination in args.template:
        TC_CONFIG.templates.append([templatefile, destination])

for templatefile, destination in TC_CONFIG.templates:
    if not os.path.isfile(templatefile):
        print(styles.FAIL + styles.BOLD + " ### ERROR: provided template file-- \"" +
              templatefile + "\" does not exist!" + styles.ENDC)
        exit(1)

if tunnel_ip:
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

if verbose > 2:
    print("Arguments:")
    print(args)

if verbose > 2:
    print("relpath_to_me: {}".format(TC_CONFIG.relpath_to_me))

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
def remove_generated_files():
    if display_datastructures:
        return
    if verbose > 2:
        print("Removing existing DHCP FILE...")
    if os.path.isfile(dhcp_mac_file):
        os.remove(dhcp_mac_file)


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

    renderer = Renderer(TC_CONFIG)
    devices = renderer.populate_data_structures(inventory)

    remove_generated_files()

    try:
        renderer.render_jinja_templates(devices)
    except RenderError as err:
        print(styles.FAIL + styles.BOLD + str(err.message) + styles.ENDC)
        exit(1)
    if display_datastructures:
        exit(0)

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
