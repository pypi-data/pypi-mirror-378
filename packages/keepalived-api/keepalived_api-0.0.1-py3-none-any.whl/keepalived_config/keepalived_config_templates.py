import copy
from keepalived_config.keepalived_config_constants import KeepAlivedConfigConstants
from keepalived_config.keepalived_config_param import KeepAlivedConfigParam
from keepalived_config.keepalived_config_block import KeepAlivedConfigBlock
from keepalived_config.keepalived_config_comment import (
    KeepAlivedConfigComment,
    KeepAlivedConfigCommentTypes,
)


class KeepAlivedConfigTemplates:
    # Common configuration templates
    TEMPLATES = {
        "basic_vrrp": {
            "type": "vrrp_instance",
            "params": {
                "state": "VRRP_STATE",
                "interface": "INTERFACE_NAME",
                "virtual_router_id": "VRRP_ROUTER_ID",
                "priority": "VRRP_PRIORITY",
                "advert_int": "VRRP_ADVERT_INT",
                "authentication": {
                    "auth_type": "PASS",
                    "auth_pass": "GENERATE_SECURE_PASSWORD"
                },
                "virtual_ipaddress": ["VIRTUAL_IP_ADDRESS"]
            }
        },
        "basic_global": {
            "type": "global_defs",
            "params": {
                "notification_email": ["NOTIFICATION_EMAIL"],
                "notification_email_from": "NOTIFICATION_EMAIL_FROM",
                "smtp_server": "SMTP_SERVER",
                "smtp_connect_timeout": 30
            }
        },
        "complete_vrrp_master": {
            "type": "vrrp_instance",
            "params": {
                "state": "MASTER",
                "interface": "INTERFACE_NAME",
                "virtual_router_id": "VRRP_ROUTER_ID",
                "priority": "VRRP_PRIORITY",
                "advert_int": "VRRP_ADVERT_INT",
                "authentication": {
                    "auth_type": "PASS",
                    "auth_pass": "GENERATE_SECURE_PASSWORD"
                },
                "virtual_ipaddress": ["VIRTUAL_IP_ADDRESS"],
                "nopreempt": ""
            }
        },
        "complete_vrrp_backup": {
            "type": "vrrp_instance",
            "params": {
                "state": "BACKUP",
                "interface": "INTERFACE_NAME",
                "virtual_router_id": "VRRP_ROUTER_ID",
                "priority": "VRRP_PRIORITY",
                "advert_int": "VRRP_ADVERT_INT",
                "authentication": {
                    "auth_type": "PASS",
                    "auth_pass": "GENERATE_SECURE_PASSWORD"
                },
                "virtual_ipaddress": ["VIRTUAL_IP_ADDRESS"]
            }
        },
        "basic_virtual_server": {
            "type": "virtual_server",
            "params": {
                "delay_loop": "VIRTUAL_SERVER_DELAY_LOOP",
                "lb_algo": "VIRTUAL_SERVER_LB_ALGO",
                "lb_kind": "VIRTUAL_SERVER_LB_KIND",
                "protocol": "VIRTUAL_SERVER_PROTOCOL",
                "real_server": {
                    "ip": "REAL_SERVER_IP",
                    "port": "REAL_SERVER_PORT",
                    "weight": "REAL_SERVER_WEIGHT",
                    "health_check": "VIRTUAL_SERVER_HEALTH_CHECK_TYPE",  # TCP_CHECK or HTTP_GET or UDP_CHECK
                    "TCP_CHECK": {
                        "connect_timeout": "TCP_CHECK_CONNECT_TIMEOUT",
                        "delay_before_retry": "TCP_CHECK_DELAY_BEFORE_RETRY"
                    },
                    "HTTP_GET": {
                        "url": "HTTP_CHECK_URL",
                        "digest": "HTTP_CHECK_DIGEST",
                        "status_code": "HTTP_CHECK_STATUS_CODE"
                    },
                    "UDP_CHECK": {
                        "connect_timeout": "UDP_CHECK_CONNECT_TIMEOUT",
                        "delay_before_retry": "UDP_CHECK_DELAY_BEFORE_RETRY"
                    }
                }
            }
        }
    }

    @classmethod
    def from_template(cls, template_name: str, instance_name: str = None, config_class=None) -> "KeepAlivedConfig":
        """
        Create configuration from template
        
        Args:
            template_name (str): Template name
            instance_name (str): Instance name (required for VRRP templates)
            config_class: The KeepAlivedConfig class to create instance from
            
        Returns:
            KeepAlivedConfig: Configuration object created based on template
        """
        if template_name not in cls.TEMPLATES:
            raise ValueError(f"Template '{template_name}' not found. Available templates: {list(cls.TEMPLATES.keys())}")
            
        template = cls.TEMPLATES[template_name]
        config = config_class()
        
        # Special handling for virtual_server template
        if template_name == "basic_virtual_server":
            block = KeepAlivedConfigBlock(template["type"], instance_name or "VIRTUAL_IP PORT")
            
            # Add basic parameters
            for param_name, param_value in template["params"].items():
                if param_name == "real_server":
                    # Process real_server using the helper method
                    real_server_block = cls._process_real_server(param_value)
                    block.add_param(real_server_block)
                else:
                    block.add_param(KeepAlivedConfigParam(param_name, str(param_value)))
            config.params.append(block)
            return config
            
        # Handle VRRP templates
        if template["type"] == "vrrp_instance":
            if not instance_name:
                raise ValueError("Instance name is required for VRRP instance templates")
            block = KeepAlivedConfigBlock(template["type"], instance_name)
        else:
            block = KeepAlivedConfigBlock(template["type"])
        
        # Add parameters from template
        for param_name, param_value in template["params"].items():
            if isinstance(param_value, dict):
                # Nested blocks
                if param_name == "real_server":
                    # Special handling for real_server using the helper method
                    real_server_block = cls._process_real_server(param_value)
                    block.add_param(real_server_block)
                else:
                    sub_block = KeepAlivedConfigBlock(param_name)
                    for sub_param_name, sub_param_value in param_value.items():
                        # Handle authentication password
                        if param_name == "authentication" and sub_param_name == "auth_pass":
                            if sub_param_value == "GENERATE_SECURE_PASSWORD":
                                # In a real implementation, you might want to generate a secure password
                                # For now, we'll use a placeholder
                                sub_block.add_param(KeepAlivedConfigParam(sub_param_name, "CHANGEME"))
                            else:
                                sub_block.add_param(KeepAlivedConfigParam(sub_param_name, str(sub_param_value)))
                        else:
                            sub_block.add_param(KeepAlivedConfigParam(sub_param_name, str(sub_param_value)))
                    block.add_param(sub_block)
            elif isinstance(param_value, list):
                # List parameters
                if param_name == "virtual_ipaddress":
                    if "VIRTUAL_IP_ADDRESS" in param_value:
                        # Placeholder for virtual IP address
                        sub_block = KeepAlivedConfigBlock(param_name)
                        sub_block.add_param(KeepAlivedConfigParam("", "VIRTUAL_IP_ADDRESS/PREFIX"))
                        block.add_param(sub_block)
                    else:
                        sub_block = KeepAlivedConfigBlock(param_name)
                        for ip in param_value:
                            sub_block.add_param(KeepAlivedConfigParam("", ip))
                        block.add_param(sub_block)
                elif param_name == "notification_email":
                    if "NOTIFICATION_EMAIL" in param_value:
                        # Placeholder for notification email
                        sub_block = KeepAlivedConfigBlock(param_name)
                        sub_block.add_param(KeepAlivedConfigParam("", "NOTIFICATION_EMAIL"))
                        block.add_param(sub_block)
                    else:
                        sub_block = KeepAlivedConfigBlock(param_name)
                        for email in param_value:
                            sub_block.add_param(KeepAlivedConfigParam("", email))
                        block.add_param(sub_block)
            else:
                # Simple parameters
                if param_value == "":
                    block.add_param(KeepAlivedConfigParam(param_name))
                elif param_value == "INTERFACE_NAME":
                    block.add_param(KeepAlivedConfigParam(param_name, "INTERFACE_NAME"))
                elif param_value == "NOTIFICATION_EMAIL":
                    block.add_param(KeepAlivedConfigParam(param_name, "NOTIFICATION_EMAIL"))
                elif param_value == "NOTIFICATION_EMAIL_FROM":
                    block.add_param(KeepAlivedConfigParam(param_name, "NOTIFICATION_EMAIL_FROM"))
                elif param_value == "SMTP_SERVER":
                    block.add_param(KeepAlivedConfigParam(param_name, "SMTP_SERVER"))
                elif param_value == "VRRP_STATE":
                    block.add_param(KeepAlivedConfigParam(param_name, "VRRP_STATE"))
                elif param_value == "VRRP_ROUTER_ID":
                    block.add_param(KeepAlivedConfigParam(param_name, "VRRP_ROUTER_ID"))
                elif param_value == "VRRP_PRIORITY":
                    block.add_param(KeepAlivedConfigParam(param_name, "VRRP_PRIORITY"))
                elif param_value == "VRRP_ADVERT_INT":
                    block.add_param(KeepAlivedConfigParam(param_name, "VRRP_ADVERT_INT"))
                elif param_value == "VIRTUAL_SERVER_DELAY_LOOP":
                    block.add_param(KeepAlivedConfigParam(param_name, "VIRTUAL_SERVER_DELAY_LOOP"))
                elif param_value == "VIRTUAL_SERVER_LB_ALGO":
                    block.add_param(KeepAlivedConfigParam(param_name, "VIRTUAL_SERVER_LB_ALGO"))
                elif param_value == "VIRTUAL_SERVER_LB_KIND":
                    block.add_param(KeepAlivedConfigParam(param_name, "VIRTUAL_SERVER_LB_KIND"))
                elif param_value == "VIRTUAL_SERVER_PROTOCOL":
                    block.add_param(KeepAlivedConfigParam(param_name, "VIRTUAL_SERVER_PROTOCOL"))
                elif param_value == "REAL_SERVER_WEIGHT":
                    block.add_param(KeepAlivedConfigParam(param_name, "REAL_SERVER_WEIGHT"))
                else:
                    block.add_param(KeepAlivedConfigParam(param_name, str(param_value)))
        
        config.params.append(block)
        return config

    @staticmethod
    def _process_real_server(real_server_config):
        """
        Process real_server configuration and create the corresponding block
        
        Args:
            real_server_config (dict): Real server configuration
            
        Returns:
            KeepAlivedConfigBlock: Real server block
        """
        real_server_block = KeepAlivedConfigBlock("real_server", 
                                                  f"{real_server_config['ip']} {real_server_config['port']}")
        real_server_block.add_param(KeepAlivedConfigParam("weight", str(real_server_config["weight"])))
        
        # Add health check block based on health_check type
        health_check_type = real_server_config.get("health_check", "TCP_CHECK")
        if health_check_type == "tcp_check" or health_check_type == "TCP_CHECK":
            # Add TCP_CHECK block
            tcp_check_block = KeepAlivedConfigBlock("TCP_CHECK")
            tcp_check_params = real_server_config["TCP_CHECK"]
            for tcp_param_name, tcp_param_value in tcp_check_params.items():
                tcp_check_block.add_param(KeepAlivedConfigParam(tcp_param_name, str(tcp_param_value)))
            real_server_block.add_param(tcp_check_block)
        elif health_check_type == "http_check" or health_check_type == "HTTP_GET":
            # Add HTTP_GET block
            http_check_block = KeepAlivedConfigBlock("HTTP_GET")
            http_check_params = real_server_config["HTTP_GET"]
            for http_param_name, http_param_value in http_check_params.items():
                http_check_block.add_param(KeepAlivedConfigParam(http_param_name, str(http_param_value)))
            real_server_block.add_param(http_check_block)
        elif health_check_type == "UDP_CHECK":
            # Add UDP_CHECK block
            udp_check_block = KeepAlivedConfigBlock("UDP_CHECK")
            udp_check_params = real_server_config["UDP_CHECK"]
            for udp_param_name, udp_param_value in udp_check_params.items():
                udp_check_block.add_param(KeepAlivedConfigParam(udp_param_name, str(udp_param_value)))
            real_server_block.add_param(udp_check_block)
        elif health_check_type == "VIRTUAL_SERVER_HEALTH_CHECK_TYPE":
            # Placeholder for health check type
            # Add both as examples
            tcp_check_block = KeepAlivedConfigBlock("TCP_CHECK")
            tcp_check_params = real_server_config["TCP_CHECK"]
            for tcp_param_name, tcp_param_value in tcp_check_params.items():
                tcp_check_block.add_param(KeepAlivedConfigParam(tcp_param_name, str(tcp_param_value)))
            real_server_block.add_param(tcp_check_block)
            
            http_check_block = KeepAlivedConfigBlock("HTTP_GET")
            http_check_params = real_server_config["HTTP_GET"]
            for http_param_name, http_param_value in http_check_params.items():
                http_check_block.add_param(KeepAlivedConfigParam(http_param_name, str(http_param_value)))
            real_server_block.add_param(http_check_block)
            
            udp_check_block = KeepAlivedConfigBlock("UDP_CHECK")
            udp_check_params = real_server_config["UDP_CHECK"]
            for udp_param_name, udp_param_value in udp_check_params.items():
                udp_check_block.add_param(KeepAlivedConfigParam(udp_param_name, str(udp_param_value)))
            real_server_block.add_param(udp_check_block)
            
        return real_server_block

    @classmethod
    def register_template(cls, template_name: str, template_definition: dict):
        """
        Register a new template or override an existing one
        
        Args:
            template_name (str): Name of the template
            template_definition (dict): Template definition with type and params
        """
        if not isinstance(template_definition, dict):
            raise ValueError("Template definition must be a dictionary")
            
        if "type" not in template_definition or "params" not in template_definition:
            raise ValueError("Template definition must contain 'type' and 'params' keys")
            
        cls.TEMPLATES[template_name] = template_definition

    @classmethod
    def list_templates(cls) -> list:
        """
        List all available templates
        
        Returns:
            list: List of template names
        """
        return list(cls.TEMPLATES.keys())