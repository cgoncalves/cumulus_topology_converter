"""
The TcConfig module represents a configuration set needed for running Topology Converter
"""
import os
import sys

class TcConfig:
    """
    Provides configuration options with defaults for TopologyConverter. An instance of this class
    can be passed around to various functions to maintain a standard configuration across modules.
    """
    def __init__(self, **kwargs):
        clean_kwargs = {k:v for k, v in kwargs.items() if v is not None} # remove null kwargs
        default_relpath_to_me = os.path.relpath(os.path.dirname(os.path.abspath(__file__)),
                                                os.getcwd())
        default_template_storage = clean_kwargs.get('template_storage', './templates')
        if not os.path.isdir(default_template_storage):
            default_template_storage = './topology_converter/templates'
        if not os.path.isdir(default_template_storage):
            default_template_storage = default_relpath_to_me + '/templates'

        self.ansible_hostfile = clean_kwargs.get('ansible_hostfile', False)
        self.arg_string = clean_kwargs.get('arg_string', ' '.join(sys.argv))
        self.create_mgmt_configs_only = clean_kwargs.get('create_mgmt_configs_only', False)
        self.create_mgmt_device = clean_kwargs.get('create_mgmt_device', False)
        self.create_mgmt_network = clean_kwargs.get('create_mgmt_network', False)
        self.display_datastructures = clean_kwargs.get('display_datastructures', False)
        self.function_group = clean_kwargs.get('function_group', {})
        self.mac_map = {}
        self.mgmt_destination_dir = clean_kwargs.get('function_group',
                                                     './helper_scripts/auto_mgmt_network/')
        self.network_functions = clean_kwargs.get('network_functions',
                                                  ['oob-switch', 'internet', 'exit', 'superspine',
                                                   'spine', 'leaf', 'tor'])
        self.parser = clean_kwargs.get('parser', None)
        self.port_gap = clean_kwargs.get('port_gap', 1000)
        self.prefix = clean_kwargs.get('prefix', None)
        self.provider = clean_kwargs.get('provider', 'virtualbox')
        self.relpath_to_me = clean_kwargs.get('relpath_to_me', default_relpath_to_me)
        self.script_storage = clean_kwargs.get('script_storage', './helper_scripts')
        self.start_mac = clean_kwargs.get('start_mac', '443839000000')
        self.start_port = clean_kwargs.get('start_port', 8000)
        self.synced_folder = clean_kwargs.get('synced_folder', False)
        self.template_storage = default_template_storage
        self.templates = clean_kwargs.get('template', [])
        self.tunnel_ip = clean_kwargs.get('tunnel_ip', None)
        self.topology_file = clean_kwargs.get('topology_file', '')
        self.total_memory = clean_kwargs.get('total_memory', 0)
        self.vagrant = clean_kwargs.get('vagrant', 'eth0')
        self.verbose = clean_kwargs.get('verbose', 0)
        self.version = clean_kwargs.get('version', '')
