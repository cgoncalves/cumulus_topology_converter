"""
Renderer module
"""

import os
import pprint
import time

import jinja2

from .tc_error import RenderError

class Renderer:
    """
    Provides methods for rendering Jinja2 templates
    """
    def __init__(self, config):
        self.config = config
        # Determine whether local or global templates will be used.
        if os.path.isdir('./templates'):
            self.template_storage = './templates'
        else:
            self.template_storage = self.config.relpath_to_me + '/templates'
        vagrantfile_template = self.template_storage + "/Vagrantfile.j2"
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
        Renders Jinja2 templates

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
        mgmt_destination_dir = "./helper_scripts/auto_mgmt_network/"
        if self.config.create_mgmt_device:
            # Check that MGMT Template Dir exists
            mgmt_template_dir = self.template_storage + "/auto_mgmt_network/"
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
            if not os.path.isdir(mgmt_destination_dir):
                if self.config.verbose > 2:
                    print("Making Directory for MGMT Helper Files: " + mgmt_destination_dir)

                try:
                    os.makedirs(mgmt_destination_dir)
                except:
                    raise RenderError('ERROR: Could not create output directory for mgmt ' + \
                                      'template renders!')

            # Render out the templates
            for template in mgmt_templates:
                render_destination = os.path.join(mgmt_destination_dir, template[0:-3])
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
