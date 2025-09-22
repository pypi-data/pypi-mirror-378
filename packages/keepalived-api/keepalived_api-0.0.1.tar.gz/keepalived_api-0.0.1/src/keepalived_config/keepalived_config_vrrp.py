from keepalived_config.keepalived_config_block import KeepAlivedConfigBlock
from keepalived_config.keepalived_config_param import KeepAlivedConfigParam


class KeepAlivedConfigVRRP:
    
    def add_vrrp_instance(self, root_params, instance_name: str, state: str, 
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
        # Find or create a root block to add the VRRP instance to
        root_block = None
        for param in root_params:
            if isinstance(param, KeepAlivedConfigBlock):
                root_block = param
                break
        
        # If no block exists, create a generic one
        if root_block is None:
            root_block = KeepAlivedConfigBlock("config")
            root_params.append(root_block)
            
        # Use the existing method from KeepAlivedConfigBlock
        vrrp_block = root_block.add_vrrp_instance(
            instance_name, state, interface, virtual_router_id, priority, advert_int
        )
        return root_params

    def add_multiple_vrrp_instances(self, root_params, instances: list):
        """
        Add multiple VRRP instances at once
        
        Args:
            instances (list): List of dictionaries with instance parameters
            
        Returns:
            KeepAlivedConfig: Current configuration object for method chaining
        """
        for instance in instances:
            self.add_vrrp_instance(root_params, **instance)
        return root_params

    def add_virtual_ipaddress(self, root_params, instance_name: str, ip_address: str):
        """
        Add a virtual IP address to a VRRP instance
        
        Args:
            instance_name (str): Name of the VRRP instance
            ip_address (str): IP address to add (e.g., "192.168.1.10/24")
            
        Returns:
            KeepAlivedConfig: Current configuration object for method chaining
        """
        # Find the VRRP instance
        vrrp_instances = self._filter_params(
            root_params,
            param_type=KeepAlivedConfigBlock, 
            name_pattern=f"vrrp_instance {instance_name}"
        )
        
        if not vrrp_instances:
            return root_params
            
        vrrp_instance = vrrp_instances[0]
        
        # Check if virtual_ipaddress block already exists
        vip_blocks = [p for p in vrrp_instance.params if isinstance(p, KeepAlivedConfigBlock) and p.name == "virtual_ipaddress"]
        
        if not vip_blocks:
            # Create virtual_ipaddress block
            vip_block = KeepAlivedConfigBlock("virtual_ipaddress")
            vip_block.add_param(KeepAlivedConfigParam("", ip_address))
            vrrp_instance.add_param(vip_block)
        else:
            # Add to existing virtual_ipaddress block
            vip_block = vip_blocks[0]
            vip_block.add_param(KeepAlivedConfigParam("", ip_address))
            
        return root_params

    def get_virtual_ipaddresses(self, root_params, instance_name: str) -> list:
        """
        Get all virtual IP addresses for a VRRP instance
        
        Args:
            instance_name (str): Name of the VRRP instance
            
        Returns:
            list: List of IP addresses, empty if instance not found
        """
        # Find the VRRP instance
        vrrp_instances = self._filter_params(
            root_params,
            param_type=KeepAlivedConfigBlock, 
            name_pattern=f"vrrp_instance {instance_name}"
        )
        
        if not vrrp_instances:
            return []
            
        vrrp_instance = vrrp_instances[0]
        
        # Find virtual_ipaddress block
        vip_blocks = [p for p in vrrp_instance.params if isinstance(p, KeepAlivedConfigBlock) and p.name == "virtual_ipaddress"]
        
        if not vip_blocks:
            return []
            
        vip_block = vip_blocks[0]
        
        # Extract IP addresses
        ip_addresses = []
        for param in vip_block.params:
            if isinstance(param, KeepAlivedConfigParam) and param.name == "":
                ip_addresses.append(param.value)
                
        return ip_addresses

    def _filter_params(self, config_params, param_type=None, name_pattern=None):
        """
        Filter configuration parameters by type or name pattern
        
        Args:
            param_type (type): Parameter type (KeepAlivedConfigParam or KeepAlivedConfigBlock)
            name_pattern (str): Name matching pattern
            
        Returns:
            list: Filtered parameter list
        """
        result = []
        
        def _filter_recursive(items):
            for item in items:
                match = True
                
                # Filter by type
                if param_type and not isinstance(item, param_type):
                    match = False
                    
                # Filter by name pattern
                if name_pattern and hasattr(item, 'name'):
                    import re
                    if not re.search(name_pattern, item.name):
                        match = False
                        
                if match:
                    result.append(item)
                    
                # Recursively process nested parameters
                if hasattr(item, 'params'):
                    _filter_recursive(item.params)
        
        _filter_recursive(config_params)
        return result