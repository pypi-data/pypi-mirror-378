from keepalived_config.keepalived_config_block import KeepAlivedConfigBlock
from keepalived_config.keepalived_config_param import KeepAlivedConfigParam


class KeepAlivedConfigVirtualServer:
    
    def add_virtual_server(self, root_params, ip: str, port: int, delay_loop: int = 6, 
                          lb_algo: str = "rr", lb_kind: str = "DR", 
                          protocol: str = "TCP"):
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
        virtual_server_block = KeepAlivedConfigBlock("virtual_server", f"{ip} {port}")
        virtual_server_block.add_param(KeepAlivedConfigParam("delay_loop", str(delay_loop)))
        virtual_server_block.add_param(KeepAlivedConfigParam("lb_algo", lb_algo))
        virtual_server_block.add_param(KeepAlivedConfigParam("lb_kind", lb_kind))
        virtual_server_block.add_param(KeepAlivedConfigParam("protocol", protocol))
        
        root_params.append(virtual_server_block)
        return root_params

    def add_real_server(self, root_params, virtual_server_ip: str, virtual_server_port: int,
                       real_server_ip: str, real_server_port: int,
                       weight: int = 1, health_check: str = "tcp_check"):
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
        # Find the virtual server
        virtual_server_name = f"virtual_server {virtual_server_ip} {virtual_server_port}"
        virtual_servers = self._filter_params(
            root_params,
            param_type=KeepAlivedConfigBlock,
            name_pattern=virtual_server_name
        )
        
        if not virtual_servers:
            # Create virtual server if it doesn't exist
            self.add_virtual_server(root_params, virtual_server_ip, virtual_server_port)
            virtual_servers = self._filter_params(
                root_params,
                param_type=KeepAlivedConfigBlock,
                name_pattern=virtual_server_name
            )
            
        virtual_server = virtual_servers[0]
        
        # Add real server
        real_server_block = KeepAlivedConfigBlock("real_server", f"{real_server_ip} {real_server_port}")
        real_server_block.add_param(KeepAlivedConfigParam("weight", str(weight)))
        
        # Add health check
        if health_check == "tcp_check":
            health_check_block = KeepAlivedConfigBlock("TCP_CHECK")
            health_check_block.add_param(KeepAlivedConfigParam("connect_timeout", "3"))
            health_check_block.add_param(KeepAlivedConfigParam("nb_get_retry", "3"))
            health_check_block.add_param(KeepAlivedConfigParam("delay_before_retry", "3"))
        elif health_check == "http_check":
            health_check_block = KeepAlivedConfigBlock("HTTP_GET")
            health_check_block.add_param(KeepAlivedConfigParam("url", "/"))
            health_check_block.add_param(KeepAlivedConfigParam("digest", "00000000000000000000000000000000"))
        
        real_server_block.add_param(health_check_block)
        virtual_server.add_param(real_server_block)
        
        return root_params

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