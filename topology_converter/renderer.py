"""
Renderer module
"""

import os
import pprint
import re
import time

import jinja2

from .styles import styles
from .tc_error import RenderError

class Renderer:
    """
    Provides methods for rendering Jinja2 templates
    """
    def __init__(self, config):
        self.config = config
        vagrantfile_template = self.config.template_storage + "/Vagrantfile.j2"
        self.config.templates = [[vagrantfile_template, 'Vagrantfile']]
        self.epoch_time = str(int(time.time()))

    def print_datastructures(self, devices, config):
        """
        Prints the renderer's config datastructures
        """
        pp = pprint.PrettyPrinter(depth=6)
        print("\n\n######################################")
        print("   DATASTRUCTURES SENT TO TEMPLATE:")
        print("######################################\n")
        print("provider=" + str(config.provider))
        print("synced_folder=" + str(config.synced_folder))
        print("version=" + str(config.version))
        print("topology_file=" + str(config.topology_file))
        print("arg_string=" + str(config.arg_string))
        print("epoch_time=" + str(self.epoch_time))
        print("script_storage=" + str(config.script_storage))
        print("generate_ansible_hostfile=" + str(config.ansible_hostfile))
        print("create_mgmt_device=" + str(config.create_mgmt_device))
        print("function_group=")
        pp.pprint(config.function_group)
        print("network_functions=")
        pp.pprint(config.network_functions)
        print("devices=")
        pp.pprint(devices)

    def render_jinja_templates(self, devices, write_files=True):
        """
        Renders Jinja2 templates. Some templates require the devices list to be in a certain order.
        Therefore, you should build the device list via Renderer.populate_data_structures()

        Arguments:
        devices (list) - List of devices
        write_files [bool] - If True, the rendered templates will also be written to disk

        Returns:
        dict - Rendered templates in the form of {<template_file>: <rendered_template>}

        Raises tc_error.RenderError if any error occurs
        """
        if self.config.display_datastructures:
            self.print_datastructures(devices, self.config)
            return

        if self.config.verbose > 2:
            print("RENDERING JINJA TEMPLATES...")

        # Render the MGMT Network stuff
        if self.config.create_mgmt_device:
            # Check that MGMT Template Dir exists
            mgmt_template_dir = self.config.template_storage + "/auto_mgmt_network/"
            if not os.path.isdir(mgmt_template_dir):
                raise RenderError('ERROR: ' + str(mgmt_template_dir) + \
                                  ' does not exist. Cannot populate templates!')

            # Scan MGMT Template Dir for .j2 files
            mgmt_templates = []

            for file in os.listdir(mgmt_template_dir):

                if file.endswith(".j2"):
                    mgmt_templates.append(file)

            if self.config.verbose > 2:
                print(" mgmt_template_dir: {}".format(mgmt_template_dir))
                print(" detected mgmt_templates:")
                print(mgmt_templates)

            # Create output location for MGMT template files
            if write_files and not os.path.isdir(self.config.mgmt_destination_dir):
                if self.config.verbose > 2:
                    print("Making Directory for MGMT Helper Files: " + \
                          self.config.mgmt_destination_dir)

                try:
                    os.makedirs(self.config.mgmt_destination_dir)
                except:
                    raise RenderError('ERROR: Could not create output directory for mgmt ' + \
                                      'template renders!')

            # Render out the templates
            for template in mgmt_templates:
                render_destination = os.path.join(self.config.mgmt_destination_dir, template[0:-3])
                template_source = os.path.join(mgmt_template_dir, template)
                self.config.templates.append([template_source, render_destination])

        # If just rendering mgmt templates, remove Vagrantfile from list
        if self.config.create_mgmt_device and self.config.create_mgmt_configs_only:
            del self.config.templates[0]

        # Use Prefix as customer name if available
        if self.config.prefix:
            customer = self.config.prefix
        else:
            customer = os.path.basename(os.path.dirname(os.getcwd()))
        generate_ansible_hostfile = self.config.ansible_hostfile

        # Render the Templates
        rendered_templates = {}
        for templatefile, destination in self.config.templates:

            if self.config.verbose > 2:
                print("    Rendering: " + templatefile + " --> " + destination)

            template = jinja2.Template(open(templatefile).read())

            rendered_template = template.render(devices=devices,
                                                customer=customer,
                                                epoch_time=self.epoch_time,
                                                generate_ansible_hostfile=generate_ansible_hostfile,
                                                libvirt_prefix=self.config.prefix,
                                                **self.config.__dict__)

            rendered_templates[templatefile] = rendered_template
            if write_files:
                with open(destination, 'w') as outfile:
                    outfile.write(rendered_template)
        return rendered_templates

    def populate_data_structures(self, inventory):
        """
        Populates device and interface data structures in a format suitable for template parsing

        Arguments:
        inventory (dict) - Topology serialized as a dict

        Returns
        list - List of a devices suitable for template parsing
        """
        devices = []

        for device in inventory:
            inventory[device]['hostname'] = device
            devices.append(inventory[device])

        devices_clean = self.clean_datastructure(devices)

        # Create Functional Group Map
        for device in devices_clean:

            if device['function'] not in self.config.function_group:
                self.config.function_group[device['function']] = []

            self.config.function_group[device['function']].append(device['hostname'])

        return devices_clean

    def clean_datastructure(self, devices):
        """
        Sorts a device list and removes faked devices

        Arguments:
        devices (list) - Dirty data structure

        Returns
        list - Clean data structure
        """
        # Sort the devices by function
        devices.sort(key=getKeyDevices)
        for device in devices:
            device['interfaces'] = sorted_interfaces(device['interfaces'])

        if self.config.display_datastructures:
            return devices
        for device in devices:
            if self.config.verbose > 0:
                print(styles.GREEN + styles.BOLD + ">> DEVICE: " + device['hostname'] + styles.ENDC)
                print("     code: " + device['os'])

                if 'memory' in device:
                    print("     memory: " + device['memory'])

                for attribute in device:
                    if attribute == 'memory' or attribute == 'os' or attribute == 'interfaces':
                        continue
                    print("     " + str(attribute) + ": " + str(device[attribute]))

            if self.config.verbose > 1:
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

def sorted_interfaces(interface_dictionary):
    """
    Creates a sorted list of interfaces from an interfaces dictionary

    Arguments:
    interface_dictionary (dict)

    Returns
    list - Sorted list
    """
    sorted_list = []
    interface_list = []

    for link in interface_dictionary:
        sorted_list.append(link)

    sorted_list.sort(key=natural_sort_key)

    for link in sorted_list:
        interface_dictionary[link]["local_interface"] = link
        interface_list.append(interface_dictionary[link])

    return interface_list

def getKeyDevices(device):
    """ Used to order the devices for printing into the vagrantfile """
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

def natural_sort_key(s):
    """ Sort function for sorting interface lists """
    _nsre = re.compile('([0-9]+)')
    if s == 'eth0': return ['A',0,'']
    return [int(text) if text.isdigit() else text.lower()
            for text in re.split(_nsre, s)]
