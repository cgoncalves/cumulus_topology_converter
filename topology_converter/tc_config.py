"""
The TcConfig module represents a configuration set needed for running Topology Converter
"""
import sys

class TcConfig:
    """
    Provides configuration options with defaults for TopologyConverter. An instance of this class
    can be passed around to various functions to maintain a standard configuration across modules.
    """
    def __init__(self, **kwargs):
        clean_kwargs = {k:v for k, v in kwargs.items() if v is not None} # remove null kwargs

        self.ansible_hostfile = clean_kwargs.get('ansible_hostfile', False)
        self.arg_string = clean_kwargs.get('arg_string', ' '.join(sys.argv))
        self.create_mgmt_configs_only = clean_kwargs.get('create_mgmt_configs_only', False)
        self.create_mgmt_device = clean_kwargs.get('create_mgmt_device', False)
        self.create_mgmt_network = clean_kwargs.get('create_mgmt_network', False)
        self.display_datastructures = clean_kwargs.get('display_datastructures', False)
        self.function_group = clean_kwargs.get('function_group', {})
        self.mac_map = {}
        self.network_functions = clean_kwargs.get('network_functions',
                                                  ['oob-switch', 'internet', 'exit', 'superspine',
                                                   'spine', 'leaf', 'tor'])
        self.parser = clean_kwargs.get('parser', None)
        self.port_gap = clean_kwargs.get('port_gap', 1000)
        self.prefix = clean_kwargs.get('prefix', None)
        self.provider = clean_kwargs.get('provider', 'virtualbox')
        self.script_storage = clean_kwargs.get('script_storage', './helper_scripts')
        self.start_mac = clean_kwargs.get('start_mac', '443839000000')
        self.start_port = clean_kwargs.get('start_port', 8000)
        self.synced_folder = clean_kwargs.get('synced_folder', False)
        self.tunnel_ip = clean_kwargs.get('tunnel_ip', None)
        self.total_memory = clean_kwargs.get('total_memory', 0)
        self.vagrant = clean_kwargs.get('vagrant', 'eth0')
        self.verbose = clean_kwargs.get('verbose', 0)
