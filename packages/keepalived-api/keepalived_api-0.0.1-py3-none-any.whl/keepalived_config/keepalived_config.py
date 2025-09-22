import os
import copy
import json

from keepalived_config.keepalived_config_constants import KeepAlivedConfigConstants
from keepalived_config.keepalived_config_param import KeepAlivedConfigParam
from keepalived_config.keepalived_config_block import KeepAlivedConfigBlock
from keepalived_config.keepalived_config_comment import (
    KeepAlivedConfigComment,
    KeepAlivedConfigCommentTypes,
)
# Import new modules
from keepalived_config.keepalived_config_templates import KeepAlivedConfigTemplates
from keepalived_config.keepalived_config_operations import KeepAlivedConfigOperations
from keepalived_config.keepalived_config_vrrp import KeepAlivedConfigVRRP
from keepalived_config.keepalived_config_virtual_server import KeepAlivedConfigVirtualServer
from keepalived_config.keepalived_config_exceptions import (
    KeepAlivedConfigError,
    KeepAlivedConfigValidationError
)
# Delayed import to avoid circular imports
# from keepalived_config.keepalived_config_parser import KeepAlivedConfigParser


class KeepAlivedConfig:
    def __init__(self, params: list = None, config_file=None):
        self._config_file = None
        self._params: list[KeepAlivedConfigBlock | KeepAlivedConfigParam] = []

        if config_file:
            self.config_file = config_file

        if params:
            self.set_params(params)

    @classmethod
    def from_file(cls, config_file_path: str) -> "KeepAlivedConfig":
        """
        Static method to load configuration directly from a config file
        
        Args:
            config_file_path (str): Configuration file path
            
        Returns:
            KeepAlivedConfig: Loaded configuration object
            
        Raises:
            FileNotFoundError: When the configuration file does not exist
        """
        # Delayed import to avoid circular imports
        from keepalived_config.keepalived_config_parser import KeepAlivedConfigParser
        parser = KeepAlivedConfigParser()
        return parser.parse_file(config_file_path)

    @classmethod
    def from_template(cls, template_name: str, instance_name: str = None) -> "KeepAlivedConfig":
        """
        Create configuration from template
        
        Args:
            template_name (str): Template name
            instance_name (str): Instance name (required for VRRP templates)
            
        Returns:
            KeepAlivedConfig: Configuration object created based on template
        """
        return KeepAlivedConfigTemplates.from_template(template_name, instance_name, cls)

    @classmethod
    def register_template(cls, template_name: str, template_definition: dict):
        """
        Register a new template or override an existing one
        
        Args:
            template_name (str): Name of the template
            template_definition (dict): Template definition with type and params
        """
        KeepAlivedConfigTemplates.register_template(template_name, template_definition)

    @classmethod
    def list_templates(cls) -> list:
        """
        List all available templates
        
        Returns:
            list: List of template names
        """
        return KeepAlivedConfigTemplates.list_templates()

    TEMPLATES = KeepAlivedConfigTemplates.TEMPLATES

    def to_dict(self) -> dict:
        """
        Convert configuration to dictionary format
        
        Returns:
            dict: Dictionary representation of configuration
        """
        operations = KeepAlivedConfigOperations()
        return operations.to_dict(self._params)

    def to_json(self) -> str:
        """
        Export configuration as JSON format
        
        Returns:
            str: Configuration string in JSON format
        """
        operations = KeepAlivedConfigOperations()
        return operations.to_json(self._params)

    def merge(self, other_config: "KeepAlivedConfig") -> "KeepAlivedConfig":
        """
        Merge another configuration into the current configuration
        
        Args:
            other_config (KeepAlivedConfig): Configuration object to merge
            
        Returns:
            KeepAlivedConfig: New configuration object after merging
        """
        operations = KeepAlivedConfigOperations()
        merged_params = operations.merge(self._params, other_config._params)
        merged_config = self.clone()
        merged_config._params = merged_params
        return merged_config

    def apply_template_params(self, param_mapping: dict) -> "KeepAlivedConfig":
        """
        Apply parameters to a template-based configuration by replacing placeholders
        
        Args:
            param_mapping (dict): Dictionary mapping placeholder names to actual values
            
        Returns:
            KeepAlivedConfig: Current configuration object for method chaining
            
        Raises:
            TypeError: If param_mapping is not a dictionary
        """
        operations = KeepAlivedConfigOperations()
        self._params = operations.apply_template_params(self._params, param_mapping)
        return self

    def format_config(self, indent_level=0, indent_size=None):
        """
        Format the configuration as a string with proper indentation
        
        Args:
            indent_level (int): Starting indentation level, default is 0
            indent_size (int): Size of each indent level, default is from constants
            
        Returns:
            str: Formatted configuration string
        """
        if indent_size is None:
            indent_size = KeepAlivedConfigConstants.INDENT_SIZE
            
        Str = ""
        for param in self._params:
            if isinstance(param, KeepAlivedConfigBlock):
                Str += param.to_str(indent_level, indent_size) + "\n"
            elif isinstance(param, KeepAlivedConfigParam):
                # Temporarily override indent size for this parameter
                original_indent_size = KeepAlivedConfigConstants.INDENT_SIZE
                KeepAlivedConfigConstants.INDENT_SIZE = indent_size
                try:
                    Str += param.to_str(indent_level) + "\n"
                finally:
                    # Restore original indent size
                    KeepAlivedConfigConstants.INDENT_SIZE = original_indent_size
            else:
                Str += str(param) + "\n"
        return Str.rstrip()
    
    def clone(self) -> "KeepAlivedConfig":
        """
        Clone the current configuration object
        
        Returns:
            KeepAlivedConfig: New copy of the configuration object
        """
        operations = KeepAlivedConfigOperations()
        cloned_config = KeepAlivedConfig()
        cloned_config._config_file = self._config_file
        cloned_config._params = operations.clone(self._params)
        return cloned_config

    def validate(self) -> list:
        """
        Validate if configuration conforms to keepalived syntax specifications
        
        Returns:
            list: List of error messages
        """
        operations = KeepAlivedConfigOperations()
        return operations.validate(self._params)

    def filter_params(self, param_type=None, name_pattern=None):
        """
        Filter configuration parameters by type or name pattern
        
        Args:
            param_type (type): Parameter type (KeepAlivedConfigParam or KeepAlivedConfigBlock)
            name_pattern (str): Name matching pattern
            
        Returns:
            list: Filtered parameter list
        """
        operations = KeepAlivedConfigOperations()
        return operations.filter_params(self._params, param_type, name_pattern)

    def traverse(self, visit_func, order="dfs"):
        """
        Traverse configuration items
        
        Args:
            visit_func (function): Visit function that accepts one parameter (configuration item)
            order (str): Traversal order, "dfs" means depth-first, "bfs" means breadth-first
        """
        operations = KeepAlivedConfigOperations()
        return operations.traverse(self._params, visit_func, order)

    def xpath(self, path: str) -> list:
        """
        Find parameters using XPath-like expressions
        
        Args:
            path (str): XPath-like expression to search for
            
        Returns:
            list: List of matching parameters
        """
        operations = KeepAlivedConfigOperations()
        return operations.xpath(self._params, path)

    def find_param(self, path: str):
        """
        Method to find configuration items by path
        
        Args:
            path (str): Configuration item path, such as "global_defs.notification_email"
            
        Returns:
            KeepAlivedConfigParam | KeepAlivedConfigBlock | None: Found configuration item or None
        """
        operations = KeepAlivedConfigOperations()
        return operations.find_param(self._params, path)

    @property
    def params(self):
        return self._params

    def set_params(self, params: list):
        if not isinstance(params, list):
            raise TypeError(f"Invalid params type '{type(params)}'! Expected 'list'")

        if list(
            filter(
                lambda c: not isinstance(c, KeepAlivedConfigParam)
                and not isinstance(c, KeepAlivedConfigBlock),
                params,
            )
        ):
            raise ValueError(
                f"Invalid params list! Expected list of {KeepAlivedConfigParam.__class__.__name__}' or {KeepAlivedConfigBlock.__class__.__name__}"
            )

        self._params = params

    @property
    def config_file(self):
        return self._config_file

    @config_file.setter
    def config_file(self, config_file: str):
        if not isinstance(config_file, str):
            raise TypeError(
                f"Invalid config_file type '{type(config_file)}'! Expected 'str'"
            )

        if not os.path.exists(config_file):
            raise FileNotFoundError(f"Config file '{config_file}' not found!")

        self._config_file = config_file

    def save(self, file=None):
        if not file:
            file = self.config_file

        with open(file, "w") as f:
            for item in self._params:
                f.write(item.to_str() + "\n")
    
    def __enter__(self):
        """Context manager entry, supports with statement"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit, supports with statement"""
        if self._config_file and exc_type is None:
            # Save configuration if no exception and config file exists
            self.save()
        # Return None to indicate not suppressing exceptions

    def add_param(self, param):
        """
        Add a parameter to the configuration
        
        Args:
            param: Parameter to add (KeepAlivedConfigParam or KeepAlivedConfigBlock)
            
        Returns:
            KeepAlivedConfig: Self for method chaining
        """
        if not isinstance(param, (KeepAlivedConfigParam, KeepAlivedConfigBlock)):
            raise TypeError(
                f"Invalid param type '{type(param)}'! Expected 'KeepAlivedConfigParam' or 'KeepAlivedConfigBlock'"
            )
        self._params.append(param)
        return self  # Return self for method chaining

    def add_vrrp_instance(self, instance_name: str, state: str, 
                         interface: str, virtual_router_id: int,
                         priority: int, advert_int: int = 1):
        """
        Convenient method to add VRRP instance to the configuration
        
        Args:
            instance_name (str): Instance name
            state (str): State (MASTER/BACKUP)
            interface (str): Network interface
            virtual_router_id (int): Virtual router ID (1-255)
            priority (int): Priority (1-255)
            advert_int (int): Advertisement interval (1-255), default is 1
            
        Returns:
            KeepAlivedConfig: Current configuration object for method chaining
            
        Raises:
            ValueError: If parameters are out of valid ranges
        """
        vrrp_ops = KeepAlivedConfigVRRP()
        self._params = vrrp_ops.add_vrrp_instance(
            self._params, instance_name, state, interface, 
            virtual_router_id, priority, advert_int)
        return self

    def set_param(self, param_path: str, value):
        """
        Convenient method to set a single parameter value by path
        
        Args:
            param_path (str): Parameter path (e.g. "global_defs.router_id")
            value: Parameter value
            
        Returns:
            KeepAlivedConfig: Self for method chaining
            
        Raises:
            KeepAlivedConfigValidationError: If parameter validation fails
        """
        # Validate parameter value
        param_parts = param_path.split(".")
        if param_parts:
            param_name = param_parts[-1]
            try:
                self.validate_param_value(param_name, value)
            except KeepAlivedConfigValidationError:
                # Re-raise with full path context
                raise KeepAlivedConfigValidationError(
                    f"Invalid value for parameter '{param_path}'",
                    param_path=param_path
                )
        
        param = self.find_param(param_path)
        if param:
            param.value = value
        else:
            # Create new parameter
            new_param = KeepAlivedConfigParam(param_parts[-1], str(value))
            if len(param_parts) > 1:
                # Need to find or create parent block
                parent_block = self.find_param(".".join(param_parts[:-1]))
                if parent_block and isinstance(parent_block, KeepAlivedConfigBlock):
                    parent_block.add_param(new_param)
                else:
                    raise KeepAlivedConfigError(f"Cannot find or create parent block for path: {param_path}")
            else:
                # Top-level parameter
                self.add_param(new_param)
        return self

    def set_multiple_params(self, param_updates: dict) -> "KeepAlivedConfig":
        """
        Set multiple parameters at once using a dictionary
        
        Args:
            param_updates (dict): Dictionary with parameter paths as keys and values
            
        Returns:
            KeepAlivedConfig: Current configuration object for method chaining
            
        Example:
            config.set_multiple_params({
                "global_defs.notification_email_from": "new_email@example.com",
                "vrrp_instance VI_1.priority": "150"
            })
        """
        operations = KeepAlivedConfigOperations()
        self._params = operations.set_multiple_params(self._params, param_updates)
        return self

    def get_param(self, path: str) -> KeepAlivedConfigParam | None:
        """
        Get a single parameter by path
        
        Args:
            path (str): Path to the parameter (e.g., "global_defs.router_id")
            
        Returns:
            KeepAlivedConfigParam | None: The parameter object or None if not found
        """
        operations = KeepAlivedConfigOperations()
        return operations.get_param(self._params, path)

    def has_param(self, path: str) -> bool:
        """
        Check if a parameter exists at the given path
        
        Args:
            path (str): Path to the parameter (e.g., "global_defs.router_id")
            
        Returns:
            bool: True if parameter exists, False otherwise
        """
        operations = KeepAlivedConfigOperations()
        return operations.has_param(self._params, path)

    def remove_param(self, path: str) -> bool:
        """
        Remove a parameter by path
        
        Args:
            path (str): Path to the parameter to remove
            
        Returns:
            bool: True if parameter was removed, False if not found
        """
        operations = KeepAlivedConfigOperations()
        return operations.remove_param(self._params, path)

    def add_virtual_ipaddress(self, instance_name: str, ip_address: str) -> "KeepAlivedConfig":
        """
        Add a virtual IP address to a VRRP instance
        
        Args:
            instance_name (str): Name of the VRRP instance
            ip_address (str): IP address to add (e.g., "192.168.1.10/24")
            
        Returns:
            KeepAlivedConfig: Current configuration object for method chaining
        """
        vrrp_ops = KeepAlivedConfigVRRP()
        self._params = vrrp_ops.add_virtual_ipaddress(self._params, instance_name, ip_address)
        return self

    def get_virtual_ipaddresses(self, instance_name: str) -> list:
        """
        Get all virtual IP addresses for a VRRP instance
        
        Args:
            instance_name (str): Name of the VRRP instance
            
        Returns:
            list: List of IP addresses, empty if instance not found
        """
        vrrp_ops = KeepAlivedConfigVRRP()
        return vrrp_ops.get_virtual_ipaddresses(self._params, instance_name)

    def add_multiple_vrrp_instances(self, instances: list) -> "KeepAlivedConfig":
        """
        Add multiple VRRP instances at once
        
        Args:
            instances (list): List of dictionaries with instance parameters
            
        Returns:
            KeepAlivedConfig: Current configuration object for method chaining
        """
        vrrp_ops = KeepAlivedConfigVRRP()
        self._params = vrrp_ops.add_multiple_vrrp_instances(self._params, instances)
        return self

    def add_virtual_server(self, ip: str, port: int, delay_loop: int = 6, 
                          lb_algo: str = "rr", lb_kind: str = "DR", 
                          protocol: str = "TCP") -> "KeepAlivedConfig":
        """
        Add a virtual server configuration
        
        Args:
            ip (str): Virtual server IP address
            port (int): Virtual server port
            delay_loop (int): Delay loop in seconds
            lb_algo (str): Load balancing algorithm
            lb_kind (str): Load balancing kind
            protocol (str): Protocol (TCP/UDP)
            
        Returns:
            KeepAlivedConfig: Current configuration object for method chaining
        """
        virtual_server_ops = KeepAlivedConfigVirtualServer()
        self._params = virtual_server_ops.add_virtual_server(
            self._params, ip, port, delay_loop, lb_algo, lb_kind, protocol)
        return self

    def add_real_server(self, virtual_server_ip: str, virtual_server_port: int,
                       real_server_ip: str, real_server_port: int,
                       weight: int = 1, health_check: str = "tcp_check") -> "KeepAlivedConfig":
        """
        Add a real server to a virtual server
        
        Args:
            virtual_server_ip (str): Virtual server IP address
            virtual_server_port (int): Virtual server port
            real_server_ip (str): Real server IP address
            real_server_port (int): Real server port
            weight (int): Weight of the real server
            health_check (str): Health check type ("tcp_check" or "http_check")
            
        Returns:
            KeepAlivedConfig: Current configuration object for method chaining
        """
        virtual_server_ops = KeepAlivedConfigVirtualServer()
        self._params = virtual_server_ops.add_real_server(
            self._params, virtual_server_ip, virtual_server_port,
            real_server_ip, real_server_port, weight, health_check)
        return self
    
    def get_param_description(self, param_name: str) -> str:
        """
        Get the description of a configuration parameter
        
        Args:
            param_name (str): Name of the parameter
            
        Returns:
            str: Description of the parameter, or empty string if not found
        """
        return KeepAlivedConfigConstants.PARAM_DESCRIPTIONS.get(param_name, "")
    
    def validate_param_value(self, param_name: str, value) -> bool:
        """
        Validate a parameter value against its validation rules
        
        Args:
            param_name (str): Name of the parameter
            value: Value to validate
            
        Returns:
            bool: True if the value is valid, False otherwise
            
        Raises:
            KeepAlivedConfigValidationError: If validation fails with details
        """
        rules = KeepAlivedConfigConstants.PARAM_VALIDATION_RULES.get(param_name)
        if not rules:
            # No validation rules, consider it valid
            return True
            
        # Check type
        if not isinstance(value, rules.get("type")):
            try:
                # Try to convert to the expected type
                if rules.get("type") == int:
                    value = int(value)
                elif rules.get("type") == str:
                    value = str(value)
                else:
                    raise KeepAlivedConfigValidationError(
                        f"Invalid type for parameter '{param_name}'. Expected {rules.get('type')}, got {type(value)}",
                        param_path=param_name
                    )
            except (ValueError, TypeError):
                raise KeepAlivedConfigValidationError(
                    f"Invalid type for parameter '{param_name}'. Expected {rules.get('type')}, got {type(value)}",
                    param_path=param_name
                )
        
        # Check allowed values
        if "allowed" in rules and value not in rules["allowed"]:
            raise KeepAlivedConfigValidationError(
                f"Invalid value for parameter '{param_name}'. Allowed values: {rules['allowed']}",
                param_path=param_name
            )
            
        # Check min/max for numeric values
        if rules.get("type") == int:
            if "min" in rules and value < rules["min"]:
                raise KeepAlivedConfigValidationError(
                    f"Value for parameter '{param_name}' is too small. Minimum: {rules['min']}",
                    param_path=param_name
                )
            if "max" in rules and value > rules["max"]:
                raise KeepAlivedConfigValidationError(
                    f"Value for parameter '{param_name}' is too large. Maximum: {rules['max']}",
                    param_path=param_name
                )
                
        return True
