"""
This module is primarily responsible for parsing a file in DOT format into a dictionary that
represents the full topology.

The main functionality of this module is provided by the parse_topology function.
"""
import ipaddress
import os
import pprint
import random
import re

import pydotplus

from .warning_messages import WarningMessages
from .tc_error import TcError
from .styles import styles

WARNING = WarningMessages()
PP = pprint.PrettyPrinter(depth=6)

def lint_topo_file(topology_file):
    """
    Lints a topology DOT file

    Arguments:
    topology_file (str) - Path to the topology DOT file

    Raises TcError if any issues are found during linting
    """
    with open(topology_file, "r") as topo_file:
        line_list = topo_file.readlines()
        count = 0

        for line in line_list:
            count += 1
            # Try to encode into ascii
            try:
                line.encode('ascii', 'ignore')

            except UnicodeDecodeError as e:
                print(styles.FAIL + styles.BOLD +
                      " ### ERROR: Line %s:\n %s\n         --> \"%s\" \n     \
                      Has hidden unicode characters in it which prevent it \
                      from being converted to ASCII cleanly. Try manually \
                      typing it instead of copying and pasting."
                      % (count, line, re.sub(r'[^\x00-\x7F]+', '?', line)) + styles.ENDC)
                raise TcError(e)

            if line.count("\"") % 2 == 1:
                print(styles.FAIL + styles.BOLD +
                      " ### ERROR: Line %s: Has an odd \
                      number of quotation characters \
                      (\").\n     %s\n" % (count, line) + styles.ENDC)
                raise TcError()

            if line.count("'") % 2 == 1:
                print(styles.FAIL + styles.BOLD +
                      " ### ERROR: Line %s: Has an odd \
                      number of quotation characters \
                      (').\n     %s\n" % (count, line) + styles.ENDC)
                raise TcError()

            if line.count(":") == 2:
                if " -- " not in line:
                    print(styles.FAIL + styles.BOLD +
                          " ### ERROR: Line %s: Does not \
                          contain the following sequence \" -- \" \
                          to seperate the different ends of the link.\n     %s\n"
                          % (count, line) + styles.ENDC)

                    raise TcError()


def get_random_localhost_ip():
    """ Returns a random IP address in the 127.0.0.0/8 subnet """
    subnet = ipaddress.IPv4Network("127.0.0.0/8")
    bits = random.getrandbits(subnet.max_prefixlen - subnet.prefixlen)
    addr = ipaddress.IPv4Address(subnet.network_address + bits)
    return str(addr)


def mac_fetch(hostname, interface, config):
    """
    Returns the next MAC address in a sequence. Calling this function mutates/increments
    the `start_mac` variable of the provided TcConfig instance

    Arguments:
    hostname (str) - Not used
    interface (str) - Interface name (used for logging)
    config (TcConfig) - TcConfig instance
    """
    new_mac = ("%x" % (int(config.start_mac, 16) + 1)).lower()
    while new_mac in config.mac_map:
        WARNING.append(styles.WARNING + styles.BOLD +
                       "    WARNING: MF MAC Address Collision -- tried to use " +
                       new_mac + " (on " + interface + ") but it was already in use." +
                       styles.ENDC)
        config.start_mac = new_mac
        new_mac = ("%x" % (int(config.start_mac, 16) + 1)).lower()
    config.start_mac = new_mac

    if config.verbose > 2:
        print("    Fetched new MAC ADDRESS: \"%s\"" % new_mac)

    return add_mac_colon(new_mac, config)


def add_mac_colon(mac_address, config):
    """
    Formats a MAC address string with colons

    Arguments:
    mac_address (str) - MAC address string without colons
    config (TcConfig) - TcConfig instance (used to determine logging level)

    Returns:
    str - Formatted MAC address

    Usage:
    >>> add_mac_colon('000000010203', config)
    '00:00:00:01:02:03'
    """
    if config.verbose > 2:
        print("MAC ADDRESS IS: \"%s\"" % mac_address)
    return ':'.join(map(''.join, zip(*[iter(mac_address)] * 2)))


def add_link(inventory, left_device, right_device, left_interface, right_interface,
             left_mac_address, right_mac_address, net_number, config):
    """
    Builds the link structure between 2 nodes in the topology. This function mutates the provided
    inventory dict.

    Arguments:
    inventory (dict) - Dict of parsed inventory
    left_device (str) - Left device node name
    right_device (str) - Right device node name
    left_interface (str) - Left node interface name
    right_interface (str) - Right node interface name
    left_mac_address (str) - Left node interface MAC
    right_mac_address (str) - Right node interface MAC
    net_number (int) - Network number
    config (TcConfig) - TcConfig instance

    Raises TcError if a fatal error occurs
    """
    network_string = "net" + str(net_number)
    PortA = str(config.start_port + net_number)
    PortB = str(config.start_port + config.port_gap + net_number)

    if int(PortA) > int(config.start_port + config.port_gap) and config.provider == "libvirt":
        print(styles.FAIL + styles.BOLD +
              " ### ERROR: Configured Port_Gap: (" + str(config.port_gap) + ") \
              exceeds the number of links in the topology. Read the help options to fix.\n\n" +
              styles.ENDC)

        config.parser.print_help()
        raise TcError()

    # Add a Link to the Inventory for both switches

    # Add left host switchport to inventory
    if left_interface not in inventory[left_device]['interfaces']:
        inventory[left_device]['interfaces'][left_interface] = {}
        inventory[left_device]['interfaces'][left_interface]['mac'] = left_mac_address

        if left_mac_address in config.mac_map:
            print(styles.FAIL + styles.BOLD +
                  " ### ERROR -- MAC Address Collision - tried to use " +
                  left_mac_address + " on " + left_device + ":" + left_interface +
                  "\n                 but it is already in use. Check your Topology File!" +
                  styles.ENDC)
            raise TcError()

        config.mac_map[left_mac_address] = left_device + "," + left_interface

        if config.provider == "virtualbox":
            inventory[left_device]['interfaces'][left_interface]['network'] = network_string

        elif config.provider == "libvirt":
            inventory[left_device]['interfaces'][left_interface]['local_port'] = PortA
            inventory[left_device]['interfaces'][left_interface]['remote_port'] = PortB

    else:
        print(styles.FAIL + styles.BOLD + " ### ERROR -- Interface " + left_interface + " Already used on device: " + left_device + styles.ENDC)
        raise TcError()

    # Add right host switchport to inventory
    if right_device == "NOTHING":
        pass

    elif right_interface not in inventory[right_device]['interfaces']:
        inventory[right_device]['interfaces'][right_interface] = {}
        inventory[right_device]['interfaces'][right_interface]['mac'] = right_mac_address

        if right_mac_address in config.mac_map:
            print(styles.FAIL + styles.BOLD +
                  " ### ERROR -- MAC Address Collision - tried to use " +
                  right_mac_address + " on " + right_device + ":" + right_interface +
                  "\n                 but it is already in use. Check your Topology File!" +
                  styles.ENDC)

            raise TcError()

        config.mac_map[right_mac_address] = right_device + "," + right_interface

        if config.provider == "virtualbox":
            inventory[right_device]['interfaces'][right_interface]['network'] = network_string

        elif config.provider == "libvirt":
            inventory[right_device]['interfaces'][right_interface]['local_port'] = PortB
            inventory[right_device]['interfaces'][right_interface]['remote_port'] = PortA

    else:
        print(styles.FAIL + styles.BOLD +
              " ### ERROR -- Interface " + right_interface +
              " Already used on device: " + right_device + styles.ENDC)
        raise TcError()

    inventory[left_device]['interfaces'][left_interface]['remote_interface'] = right_interface
    inventory[left_device]['interfaces'][left_interface]['remote_device'] = right_device

    if right_device != "NOTHING":
        inventory[right_device]['interfaces'][right_interface]['remote_interface'] = left_interface
        inventory[right_device]['interfaces'][right_interface]['remote_device'] = left_device

    if config.provider == 'libvirt':
        if right_device != "NOTHING":
            inventory[left_device]['interfaces'][left_interface]['local_ip'] = inventory[left_device]['tunnel_ip']
            inventory[left_device]['interfaces'][left_interface]['remote_ip'] = inventory[right_device]['tunnel_ip']
            inventory[right_device]['interfaces'][right_interface]['local_ip'] = inventory[right_device]['tunnel_ip']
            inventory[right_device]['interfaces'][right_interface]['remote_ip'] = inventory[left_device]['tunnel_ip']
        elif right_device == "NOTHING":
            if config.tunnel_ip != None:
                inventory[left_device]['interfaces'][left_interface]['local_ip'] = config.tunnel_ip
                inventory[left_device]['interfaces'][left_interface]['remote_ip'] = config.tunnel_ip
            else:
                inventory[left_device]['interfaces'][left_interface]['local_ip'] = "127.0.0.1"
                inventory[left_device]['interfaces'][left_interface]['remote_ip'] = "127.0.0.1"


def parse_topology(topology_file, config):
    """
    Parses a topology file in DOT format and serializes it into a dict that contains all defined
    nodes and their links.

    Arguments:
    topology_file (str) - Path to DOT file
    config (TcConfig) - TcConfig instance

    Returns:
    dict - Serialized topology

    Raises TcError if any fatal error occurs

    Usage:
    >>> parse_topology('./topology.dot', config)
    {'oob-mgmt-switch': {'interfaces': {'swp1': {'mac': '44:38:39:00:00:01', 'network': 'net1',
                                                 'remote_interface': 'eth1',
                                                 'remote_device': 'oob-mgmt-server'}},
                         'os': 'b9164d74-3b65-4267-95a6-8bcbaccaccd6', 'memory': '768',
                         'config': './helper_scripts/oob_switch_config.sh',
                         'function': 'oob-switch', 'mgmt_ip': '192.168.200.2', 'vagrant': 'eth0'},
    ...etc...
    """
    provider = config.provider
    verbose = config.verbose
    tunnel_ip = config.tunnel_ip
    lint_topo_file(topology_file)
    try:
        topology = pydotplus.graphviz.graph_from_dot_file(topology_file)
    except Exception as e:
        print(styles.FAIL + styles.BOLD +
              " ### ERROR: Cannot parse the provided topology.dot \
              file (%s)\n     There is probably a syntax error \
              of some kind, common causes include failing to \
              close quotation marks and hidden characters from \
              copy/pasting device names into the topology file."
              % (topology_file) + styles.ENDC)

        raise TcError(e)

    inventory = {}

    # Generate a random localhost IP for libvirt tunnels (if needed)
    if tunnel_ip == 'random':
        tunnel_ip = get_random_localhost_ip()

    try:
        nodes = topology.get_node_list()

    except Exception as e:
        print(e)
        print(styles.FAIL + styles.BOLD +
              " ### ERROR: There is a syntax error in your topology file \
              (%s). Read the error output above for any clues as to the source."
              % (topology_file) + styles.ENDC)

        raise TcError()

    try:
        edges = topology.get_edge_list()

    except Exception as e:
        print(e)
        print(styles.FAIL + styles.BOLD +
              " ### ERROR: There is a syntax error in your topology file \
              (%s). Read the error output above for any clues as to the source."
              % (topology_file) + styles.ENDC)

        raise TcError(e)

    # Add Nodes to inventory
    for node in nodes:

        node_name = node.get_name().replace('"', '')

        if node_name.startswith(".") or node_name.startswith("-"):
            print(styles.FAIL + styles.BOLD +
                  " ### ERROR: Node name cannot start with a hyphen or period. \
                  '%s' is not valid!\n" % (node_name) + styles.ENDC)

            raise TcError()

        reg = re.compile('^[A-Za-z0-9\.-]+$')

        if not reg.match(node_name):
            print(styles.FAIL + styles.BOLD +
                  " ### ERROR: Node name for the \
                  VM should only contain letters, \
                  numbers, hyphens or dots. It cannot \
                  start with a hyphen or dot.  \
                  '%s' is not valid!\n" % (node_name) + styles.ENDC)

            raise TcError()

        # Try to encode into ascii
        try:
            node_name.encode('ascii', 'ignore')

        except UnicodeDecodeError as e:
            print(styles.FAIL + styles.BOLD +
                  " ### ERROR: Node name \"%s\" --> \"%s\" \
                  has hidden unicode characters in it which \
                  prevent it from being converted to Ascii cleanly. \
                  Try manually typing it instead of copying and pasting."
                  % (node_name, re.sub(r'[^\x00-\x7F]+', ' ', node_name)) + styles.ENDC)

            raise TcError()

        if node_name not in inventory:
            inventory[node_name] = {}
            inventory[node_name]['interfaces'] = {}

        node_attr_list = node.get_attributes()

        # Define Functional Defaults
        if 'function' in node_attr_list:
            value = node.get('function')

            if value.startswith('"') or value.startswith("'"):
                value = value[1:].lower()

            if value.endswith('"') or value.endswith("'"):
                value = value[:-1].lower()

            if value == 'fake':
                inventory[node_name]['os'] = "None"
                inventory[node_name]['memory'] = "1"

            if value == 'oob-server':
                inventory[node_name]['os'] = "generic/ubuntu1804"
                inventory[node_name]['memory'] = "1024"

            if value == 'oob-switch':
                inventory[node_name]['os'] = "CumulusCommunity/cumulus-vx"
                inventory[node_name]['memory'] = "768"
                inventory[node_name]['config'] = config.script_storage+"/oob_switch_config.sh"

            elif value in config.network_functions:
                inventory[node_name]['os'] = "CumulusCommunity/cumulus-vx"
                inventory[node_name]['memory'] = "768"

            elif value == 'host':
                inventory[node_name]['os'] = "generic/ubuntu1804"
                inventory[node_name]['memory'] = "512"

        if provider == 'libvirt' and 'pxehost' in node_attr_list:
            if node.get('pxehost').replace('"', '') == "True":
                inventory[node_name]['os'] = "N/A (PXEBOOT)"

        # Add attributes to node inventory
        for attribute in node_attr_list:

            if verbose > 2:
                print(attribute + " = " + node.get(attribute))

            value = node.get(attribute)

            if value.startswith('"') or value.startswith("'"):
                value = value[1:]

            if value.endswith('"') or value.endswith("'"):
                value = value[:-1]

            inventory[node_name][attribute] = value

            if (attribute == "config") and (not os.path.isfile(value)):
                WARNING.append(styles.WARNING + styles.BOLD +
                               "    WARNING: Node \"" + node_name + "\" \
                               Config file for device does not exist" + styles.ENDC)

        if provider == 'libvirt':
            if 'os' in inventory[node_name]:
                if inventory[node_name]['os'] == 'boxcutter/ubuntu1604' or inventory[node_name]['os'] == 'bento/ubuntu-16.04' or inventory[node_name]['os'] == 'ubuntu/xenial64':
                    print(styles.FAIL + styles.BOLD + " ### ERROR: device " + node_name +
                          " -- Incompatible OS for libvirt provider.")
                    print("              Do not attempt to use a mutated image for Ubuntu16.04 on Libvirt")
                    print("              use an ubuntu1604 image which is natively built for libvirt")
                    print("              like generic/ubuntu18.04.")
                    print("              See https://github.com/CumulusNetworks/topology_converter/tree/master/documentation#vagrant-box-selection")
                    print("              See https://github.com/vagrant-libvirt/vagrant-libvirt/issues/607")
                    print("              See https://github.com/vagrant-libvirt/vagrant-libvirt/issues/609" + styles.ENDC)
                    raise TcError()

        # Make sure mandatory attributes are present.
        mandatory_attributes = ['os', ]
        for attribute in mandatory_attributes:
            if attribute not in inventory[node_name]:
                print(styles.FAIL + styles.BOLD +
                      " ### ERROR: MANDATORY DEVICE ATTRIBUTE \"" + attribute + "\" \
                      not specified for " + node_name + styles.ENDC)

                raise TcError()

        # Extra Massaging for specific attributes.
        # light sanity checking.
        if 'function' not in inventory[node_name]:
            inventory[node_name]['function'] = "Unknown"

        if 'memory' in inventory[node_name]:
            try:
                if int(inventory[node_name]['memory']) <= 0:
                    print(styles.FAIL + styles.BOLD +
                          " ### ERROR -- Memory must be greater than 0mb on " +
                           node_name + styles.ENDC)
                    raise TcError()
            except:
                print(styles.FAIL + styles.BOLD +
                      " ### ERROR -- There is something wrong with the memory definition on " +
                      node_name + styles.ENDC)
                raise TcError()

        if provider == "libvirt":
            if tunnel_ip != None: inventory[node_name]['tunnel_ip'] = tunnel_ip
            elif 'tunnel_ip' not in inventory[node_name]:
                inventory[node_name]['tunnel_ip'] = '127.0.0.1'

        if 'vagrant' not in inventory[node_name]:
            inventory[node_name]['vagrant'] = config.vagrant

    # Add All the Edges to Inventory
    net_number = 1
    for edge in edges:
        # if provider == "virtualbox":
        network_string = "net" + str(net_number)

        # elif provider == "libvirt":
        PortA = str(config.start_port + net_number)
        PortB = str(config.start_port + config.port_gap + net_number)

        # Set Devices/interfaces/MAC Addresses
        left_device = edge.get_source().split(":")[0].replace('"', '')
        left_interface = edge.get_source().split(":")[1].replace('"', '')

        if "/" in left_interface:
            new_left_interface = left_interface.replace('/', '-')
            WARNING.append(styles.WARNING + styles.BOLD +
                           "    WARNING: Device %s interface %s has bad \
                           characters altering to this %s."
                           % (left_device, left_interface, new_left_interface) +
                           styles.ENDC)
            left_interface = new_left_interface

        right_device = edge.get_destination().split(":")[0].replace('"', '')
        right_interface = edge.get_destination().split(":")[1].replace('"', '')
        if "/" in right_interface:
            new_right_interface = right_interface.replace('/', '-')
            WARNING.append(styles.WARNING + styles.BOLD +
                           "    WARNING: Device %s interface %s has bad \
                           characters altering to this %s."
                           % (right_device, right_interface, new_right_interface) +
                           styles.ENDC)
            right_interface = new_right_interface

        for value in [left_device, left_interface, right_device, right_interface]:
            # Try to encode into ascii
            try:
                value.encode('ascii', 'ignore')
            except UnicodeDecodeError as e:
                print(styles.FAIL + styles.BOLD +
                      " ### ERROR: in line --> \"%s\":\"%s\" -- \"%s\":\"%s\"\n        \
                      Link component: \"%s\" has hidden unicode characters in it \
                      which prevent it from being converted to Ascii cleanly. \
                      Try manually typing it instead of copying and pasting."
                      % (left_device, left_interface, right_device, right_interface,
                         re.sub(r'[^\x00-\x7F]+', ' ', value)) + styles.ENDC)

                raise TcError()

        left_mac_address = ""

        if edge.get('left_mac') is not None:
            temp_left_mac = edge.get('left_mac').replace('"', '').replace(':', '').lower()
            left_mac_address = add_mac_colon(temp_left_mac, config)

        else:
            left_mac_address = mac_fetch(left_device, left_interface, config)

        right_mac_address = ""

        if edge.get('right_mac') is not None:
            temp_right_mac = edge.get('right_mac').replace('"', '').replace(':', '').lower()
            right_mac_address = add_mac_colon(temp_right_mac, config)

        else:
            right_mac_address = mac_fetch(right_device, right_interface, config)

        # Check to make sure each device in the edge already exists in inventory
        if left_device not in inventory:
            print(styles.FAIL + styles.BOLD + " ### ERROR: device " +
                  left_device + " is referred to in list of edges/links \
                  but not defined as a node." + styles.ENDC)

            raise TcError()

        if right_device not in inventory:
            print(styles.FAIL + styles.BOLD +
                  " ### ERROR: device " + right_device + " is referred to \
                  in list of edges/links but not defined as a node." + styles.ENDC)

            raise TcError()

        # Adds link to inventory datastructure
        add_link(inventory,
                 left_device,
                 right_device,
                 left_interface,
                 right_interface,
                 left_mac_address,
                 right_mac_address,
                 net_number,
                 config)

        # Handle Link-based Passthrough Attributes
        edge_attributes = {}
        for attribute in edge.get_attributes():
            if attribute == "left_mac" or attribute == "right_mac":
                continue

            if attribute in edge_attributes:
                WARNING.append(styles.WARNING + styles.BOLD +
                               "    WARNING: Attribute \"" + attribute +
                               "\" specified twice. Using second value." + styles.ENDC)

            value = edge.get(attribute)

            if value.startswith('"') or value.startswith("'"):
                value = value[1:]

            if value.endswith('"') or value.endswith("'"):
                value = value[:-1]

            if attribute.startswith('left_'):
                inventory[left_device]['interfaces'][left_interface][attribute[5:]] = value

            elif attribute.startswith('right_'):
                inventory[right_device]['interfaces'][right_interface][attribute[6:]] = value

            else:
                inventory[left_device]['interfaces'][left_interface][attribute] = value
                inventory[right_device]['interfaces'][right_interface][attribute] = value
                # edge_attributes[attribute]=value

        net_number += 1

    # Remove PXEbootinterface attribute from hosts which are not set to PXEboot=True
    for device in inventory:

        count = 0

        for link in inventory[device]['interfaces']:

            if 'pxebootinterface' in inventory[device]['interfaces'][link]:

                count += 1  # increment count to make sure more than one interface doesn't try to set nicbootprio

                if 'pxehost' not in inventory[device]:
                    del inventory[device]['interfaces'][link]['pxebootinterface']

                elif 'pxehost' in inventory[device]:
                    if inventory[device]['pxehost'] != "True":
                        del inventory[device]['interfaces'][link]['pxebootinterface']

    # Make sure no host has PXEbootinterface set more than once
    # Have to make two passes here because doing it in one pass could have
    # side effects.
    for device in inventory:

        count = 0

        for link in inventory[device]['interfaces']:
            if 'pxebootinterface' in inventory[device]['interfaces'][link]:
                count += 1  # increment count to make sure more than one interface doesn't try to set nicbootprio

        if count > 1:
            print(styles.FAIL + styles.BOLD +
                  " ### ERROR -- Device " + device +
                  " sets pxebootinterface more than once." +
                  styles.ENDC)

            raise TcError()

    #######################
    # Add Mgmt Network Links
    #######################
    if config.create_mgmt_device:
        mgmt_server = None
        mgmt_switch = None

        # Look for Managment Server/Switch
        for device in inventory:

            if inventory[device]["function"] == "oob-switch":
                mgmt_switch = device

            elif inventory[device]["function"] == "oob-server":
                mgmt_server = device

        if verbose > 2:
            print(" detected mgmt_server: %s" % mgmt_server)
            print("          mgmt_switch: %s" % mgmt_switch)
        # Hardcode mgmt server parameters
        if mgmt_server == None:
            if "oob-mgmt-server" in inventory:
                print(styles.FAIL + styles.BOLD + ' ### ERROR: oob-mgmt-server must be set to function = "oob-server"' + styles.ENDC)
                raise TcError()
            inventory["oob-mgmt-server"] = {}
            inventory["oob-mgmt-server"]["function"] = "oob-server"

            intf = ipaddress.ip_interface(u'192.168.200.254/24')

            inventory["oob-mgmt-server"]["interfaces"] = {}
            mgmt_server = "oob-mgmt-server"
            if provider == "libvirt":
                if tunnel_ip != None: inventory["oob-mgmt-server"]['tunnel_ip'] = tunnel_ip
                elif 'tunnel_ip' not in inventory["oob-mgmt-server"]:
                    inventory["oob-mgmt-server"]['tunnel_ip'] = '127.0.0.1'

            inventory["oob-mgmt-server"]["mgmt_ip"] = ("%s" % intf.ip)
            inventory["oob-mgmt-server"]["mgmt_network"] = ("%s" % intf.network[0])
            inventory["oob-mgmt-server"]["mgmt_cidrmask"] = ("/%s" % intf.network.prefixlen)
            inventory["oob-mgmt-server"]["mgmt_netmask"] = ("%s" % intf.netmask)
            mgmt_server == "oob-mgmt-server"

        else:
            if "mgmt_ip" not in inventory[mgmt_server]:
                intf = ipaddress.ip_interface(u'192.168.200.254/24')

            else:
                if "/" in inventory[mgmt_server]["mgmt_ip"]:
                    intf = ipaddress.ip_interface(inventory[mgmt_server]["mgmt_ip"])

                else:
                    intf = ipaddress.ip_interface(inventory[mgmt_server]["mgmt_ip"] + "/24")

            if provider == "libvirt":
                if tunnel_ip != None: inventory[mgmt_server]['tunnel_ip'] = tunnel_ip
                elif 'tunnel_ip' not in inventory[mgmt_server]:
                    inventory[mgmt_server]['tunnel_ip'] = '127.0.0.1'


            inventory[mgmt_server]["mgmt_ip"] = ("%s" % intf.ip)
            inventory[mgmt_server]["mgmt_network"] = ("%s" % intf.network[0])
            inventory[mgmt_server]["mgmt_cidrmask"] = ("/%s" % intf.network.prefixlen)
            inventory[mgmt_server]["mgmt_netmask"] = ("%s" % intf.netmask)

        try:
            inventory[mgmt_server]["mgmt_dhcp_start"] = ("%s" % intf.network[10])
            inventory[mgmt_server]["mgmt_dhcp_stop"] = ("%s" % intf.network[50])

        except IndexError:
            print(styles.FAIL + styles.BOLD +
                  " ### ERROR: Prefix Length on the Out Of Band Server \
                  is not big enough to support usage of the 10th-50th \
                  IP addresses being used for DHCP")

            raise TcError()

        if "os" not in inventory[mgmt_server]:
            inventory[mgmt_server]["os"] = "generic/ubuntu1804"

        if "memory" not in inventory[mgmt_server]:
            inventory[mgmt_server]["memory"] = "512"

        if "config" in inventory[mgmt_server]:
            print(styles.FAIL + styles.BOLD + '''
### WARNING: You have requested automatic creation of out-of-band
management network. This includes preparing the out-of-band
management server which is done by one of the helper scripts.
However, you have manually set the configuration script for the
out-of-band management server (which overrides ours). This might
result in issues if you are relying on the OOB server in your
topology. If you want all the nice things topology_converter has
for you on the OOB server then you might want to remove the
script for the device with function="oob-mgmt-server" in the
topology.dot file.

Refer to OOB_Server_Config_auto_mgmt.sh script in helper scripts
folder to see how we set up the OOB server for you..''' + styles.ENDC)

        else:
            inventory[mgmt_server]["config"] = "./helper_scripts/auto_mgmt_network/OOB_Server_Config_auto_mgmt.sh"

        # Hardcode mgmt switch parameters
        if mgmt_switch is None and config.create_mgmt_network:

            if "oob-mgmt-switch" in inventory:
                print(styles.FAIL + styles.BOLD + ' ### ERROR: oob-mgmt-switch must be set to function = "oob-switch"' + styles.ENDC)
                raise TcError()

            inventory["oob-mgmt-switch"] = {}
            inventory["oob-mgmt-switch"]["function"] = "oob-switch"
            inventory["oob-mgmt-switch"]["interfaces"] = {}

            if provider == "libvirt":
                if tunnel_ip != None: inventory["oob-mgmt-switch"]['tunnel_ip'] = tunnel_ip
                elif 'tunnel_ip' not in inventory["oob-mgmt-switch"]:
                    inventory["oob-mgmt-switch"]['tunnel_ip'] = '127.0.0.1'

            mgmt_switch = "oob-mgmt-switch"

        if config.create_mgmt_network:
            inventory[mgmt_switch]["os"] = "CumulusCommunity/cumulus-vx"
            inventory[mgmt_switch]["memory"] = "512"
            inventory[mgmt_switch]["config"] = config.script_storage+"/oob_switch_config.sh"

            # Add Link between oob-mgmt-switch oob-mgmt-server
            net_number += 1
            left_mac = mac_fetch(mgmt_switch, "swp1", config)
            right_mac = mac_fetch(mgmt_server, "eth1", config)
            if verbose > 1:
                print("  adding mgmt links:")
                if provider == "virtualbox":
                    print("    %s:%s (mac: %s) --> %s:%s (mac: %s)     network_string:%s"
                      % (mgmt_switch, "swp1", left_mac, mgmt_server, "eth1", right_mac,
                         network_string))

                elif provider == "libvirt":
                    print("    %s:%s udp_port %s (mac: %s) --> %s:%s udp_port %s (mac: %s)"
                       % (mgmt_switch, "swp1", left_mac, PortA, mgmt_server, "eth1", PortB,
                          right_mac))

            add_link(inventory,
                     mgmt_switch,
                     mgmt_server,
                     "swp1",
                     "eth1",
                     left_mac,
                     right_mac,
                     net_number,
                     config)

            mgmt_switch_swp = 1

            # Add Eth0 MGMT Link for every device that is is not oob-switch or oob-server
            for device in inventory:
                if inventory[device]["function"] == "oob-server" or inventory[device]["function"] == "oob-switch":
                    continue

                mgmt_switch_swp += 1
                net_number += 1

                if int(PortA) > int(config.start_port + config.port_gap) and provider == "libvirt":
                    print(styles.FAIL + styles.BOLD +
                          " ### ERROR: Configured Port_Gap: (" + str(config.port_gap) + ") exceeds \
                          the number of links in the topology. Read the help options to fix.\n\n" +
                          styles.ENDC)

                    config.parser.print_help()

                    raise TcError()

                mgmt_switch_swp_val = "swp" + str(mgmt_switch_swp)
                left_mac = mac_fetch(mgmt_switch, mgmt_switch_swp_val, config)
                right_mac = mac_fetch(device, "eth0", config)

                half1_exists = False
                half2_exists = False

                # Check to see if components of the link already exist
                if "eth0" in inventory[device]['interfaces']:

                    if inventory[device]['interfaces']['eth0']['remote_interface'] != mgmt_switch_swp_val:
                        print(styles.FAIL + styles.BOLD +
                              " ### ERROR: %s:eth0 interface already exists but \
                              not connected to %s:%s" % (device, mgmt_switch, mgmt_switch_swp_val) +
                              styles.ENDC)
                        raise TcError()

                    if inventory[device]['interfaces']['eth0']['remote_device'] != mgmt_switch:
                        print(styles.FAIL + styles.BOLD +
                              " ### ERROR: %s:eth0 interface already exists but \
                              not connected to %s:%s" % (device, mgmt_switch, mgmt_switch_swp_val) +
                              styles.ENDC)
                        raise TcError()

                    if verbose > 2:
                        print("        mgmt link on %s already exists and is good." % (mgmt_switch))

                    half1_exists = True

                if mgmt_switch_swp_val in inventory[mgmt_switch]['interfaces']:

                    if inventory[mgmt_switch]['interfaces'][mgmt_switch_swp_val]['remote_interface'] != "eth0":
                        print(styles.FAIL + styles.BOLD +
                              " ### ERROR: %s:%s-- link already exists but \
                              not connected to %s:eth0" % (mgmt_switch, mgmt_switch_swp_val, device) +
                              styles.ENDC)
                        raise TcError()

                    if inventory[mgmt_switch]['interfaces'][mgmt_switch_swp_val]['remote_device'] != device:
                        print(styles.FAIL + styles.BOLD +
                              " ### ERROR: %s:%s-- link already exists but \
                              not connected to %s:eth0" % (mgmt_switch, mgmt_switch_swp_val, device) +
                              styles.ENDC)
                        raise TcError()

                    if verbose > 2:
                        print("        mgmt link on %s already exists and is good." % (mgmt_switch))

                    half2_exists = True

                if not half1_exists and not half2_exists:

                    # Display add message
                    if verbose > 1:
                        if provider == "virtualbox":
                            print("    %s:%s (mac: %s) --> %s:%s (mac: %s)     network_string:net%s"
                                  % (mgmt_switch, mgmt_switch_swp_val, left_mac, device, "eth0", right_mac, net_number))

                        elif provider == "libvirt":
                            print("    %s:%s udp_port %s (mac: %s) --> %s:%s udp_port %s (mac: %s)"
                                  % (mgmt_switch, mgmt_switch_swp_val, PortA, left_mac, device, "eth0", PortB, right_mac))

                    add_link(inventory,
                             mgmt_switch,
                             device,
                             mgmt_switch_swp_val,
                             "eth0",
                             left_mac,
                             right_mac,
                             net_number,
                             config)

        # Determine Used MGMT IPs
        if verbose > 1:
            print("  MGMT_IP ADDRESS for OOB_SERVER IS: %s%s"
                  % (inventory[mgmt_server]["mgmt_ip"], inventory[mgmt_server]["mgmt_cidrmask"]))

        intf = ipaddress.ip_interface("%s%s" % (inventory[mgmt_server]["mgmt_ip"],
                                                        inventory[mgmt_server]["mgmt_cidrmask"]))
        network = ipaddress.ip_network("%s" % (intf.network))

        acceptable_host_addresses = list(intf.network.hosts())

        for device in inventory:

            if 'mgmt_ip' in inventory[device]:
                if inventory[device]['mgmt_ip'] != "":
                    if device == "oob-mgmt-server":
                        try:
                            node_mgmt_ip = ipaddress.ip_address(inventory[device]['mgmt_ip'].split('/')[0])

                        except:
                            print(styles.FAIL + styles.BOLD + " ### ERROR: Invalid IP specified in mgmt_ip option for %s" \
                                  % (device) + styles.ENDC)
                            raise TcError()
                    else:
                        try:
                            node_mgmt_ip = ipaddress.ip_address(inventory[device]['mgmt_ip'])

                        except:
                            print(styles.FAIL + styles.BOLD + " ### ERROR: Invalid IP specified in mgmt_ip option for %s" \
                                  % (device) + styles.ENDC)
                            raise TcError()
                else:
                    print(styles.FAIL + styles.BOLD + " ### ERROR: Empty value provided for mgmt_ip option for %s" \
                          % (device) + styles.ENDC)
                    raise TcError()


                # Check that Defined Mgmt_IP is in same Subnet as OOB-SERVER
                if node_mgmt_ip not in network:
                    print(styles.FAIL + styles.BOLD +
                          " ### ERROR: IP address (%s) is not in the \
                          Management Server subnet %s" % (node_mgmt_ip, network))

                    raise TcError()

                # Remove Address from Valid Assignable Address Pool
                try:
                    acceptable_host_addresses.remove(node_mgmt_ip)

                    if verbose > 2:
                        print("  INFO: Removing MGMT_IP Address %s from Assignable Pool. \
                              Address already assigned to %s" % (node_mgmt_ip, device))

                except:
                    print(styles.FAIL + styles.BOLD +
                          " ### ERROR: Cannot mark the mgmt_ip (%s) as used." % (node_mgmt_ip))

                    raise TcError()

        # Add Mgmt_IP if not configured
        for device in inventory:
            if 'mgmt_ip' not in inventory[device]:
                new_mgmt_ip = acceptable_host_addresses.pop(0)
                inventory[device]['mgmt_ip'] = "%s" % (new_mgmt_ip)
                if verbose > 1:
                    print("    Device: \"%s\" was assigned mgmt_ip %s" % (device, new_mgmt_ip))

    # Add Dummy Eth0 Link
    for device in inventory:

        if inventory[device]["function"] not in config.network_functions:
            continue

        if 'vagrant' in inventory[device]:
            if inventory[device]['vagrant'] == 'eth0':
                continue

        # Check to see if components of the link already exist
        if "eth0" not in inventory[device]['interfaces']:
            net_number += 1

            add_link(inventory,
                     device,
                     "NOTHING",
                     "eth0",
                     "NOTHING",
                     mac_fetch(device, "eth0", config),
                     "NOTHING",
                     net_number,
                     config)

    # Add Extra Port Ranges (if needed)
    for device in inventory:
        # Tally up the minimum memory usage (if specified)
        if 'memory' in inventory[device]: config.total_memory += int(inventory[device]['memory'])

        if "ports" in inventory[device] and \
            inventory[device]["function"] in config.network_functions:

            if provider != "libvirt":
                WARNING.append(styles.WARNING + styles.BOLD +
                               "    WARNING: 'ports' setting on node %s will be ignored \
                               when not using the libvirt hypervisor." % (device) +
                               styles.ENDC)

            port_range = int(inventory[device]["ports"])
            existing_port_list = []
            ports_to_create = []
            only_nums = re.compile(r'[^\d]+')
            for port in inventory[device]['interfaces']:
                existing_port_list.append(int(only_nums.sub('', port)))
            print(existing_port_list)

            for i in range(0, port_range + 1):

                if i not in existing_port_list:
                    ports_to_create.append(i)

            if verbose > 2:
                print("  INFO: On %s will create the following ports:" % (device))
                print(ports_to_create)

            # exit(1)

            for i in ports_to_create:
                net_number += 1
                add_link(inventory,
                         device,
                         "NOTHING",
                         "swp%s" % (i),
                         "NOTHING",
                         mac_fetch(device, "swp%s" % (i), config),
                         "NOTHING",
                         net_number,
                         config)

    if verbose > 2:
        print("\n\n ### Inventory Datastructure: ###")
        PP.pprint(inventory)

    return inventory
