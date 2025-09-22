from keepalived_config.keepalived_config_param import (
    KeepAlivedConfigParam,
    KeepAlivedConfigConstants,
)


class KeepAlivedConfigBlock(KeepAlivedConfigParam):
    def __init__(self, type_name: str, name: str = "", comments=None):
        if not isinstance(type_name, str):
            raise TypeError(
                f"Invalid type type_name '{type(type_name)}'! Expected 'str'"
            )

        super().__init__(
            name=f"{type_name}{' ' + name if name else ''}", value="", comments=comments
        )

        self._params: list[KeepAlivedConfigParam | KeepAlivedConfigBlock] = []

    @property
    def params(self):
        return self._params

    def add_param(self, param):
        if not isinstance(param, KeepAlivedConfigParam):
            raise TypeError(
                f"Invalid param type '{type(param)}'! Expected '{KeepAlivedConfigParam.__class__.__name__}'"
            )
        self._params.append(param)

    def add_vrrp_instance(self, instance_name: str, state: str, 
                         interface: str, virtual_router_id: int,
                         priority: int, advert_int: int = 1):
        """
        Convenient method to add VRRP instance
        
        Args:
            instance_name (str): Instance name
            state (str): State (MASTER/BACKUP)
            interface (str): Network interface
            virtual_router_id (int): Virtual router ID (1-255)
            priority (int): Priority (1-255)
            advert_int (int): Advertisement interval (1-255), default is 1
            
        Returns:
            KeepAlivedConfigBlock: Newly created VRRP instance block
            
        Raises:
            ValueError: If parameters are out of valid ranges
        """
        # Validate parameters
        if not 1 <= virtual_router_id <= 255:
            raise ValueError("virtual_router_id must be between 1 and 255")
            
        if not 1 <= priority <= 255:
            raise ValueError("priority must be between 1 and 255")
            
        if not 1 <= advert_int <= 255:
            raise ValueError("advert_int must be between 1 and 255")
            
        if state not in ["MASTER", "BACKUP"]:
            raise ValueError("state must be either 'MASTER' or 'BACKUP'")
        
        vrrp_block = KeepAlivedConfigBlock("vrrp_instance", instance_name)
        
        # Add basic parameters
        vrrp_block.add_param(KeepAlivedConfigParam("state", state))
        vrrp_block.add_param(KeepAlivedConfigParam("interface", interface))
        vrrp_block.add_param(KeepAlivedConfigParam("virtual_router_id", str(virtual_router_id)))
        vrrp_block.add_param(KeepAlivedConfigParam("priority", str(priority)))
        vrrp_block.add_param(KeepAlivedConfigParam("advert_int", str(advert_int)))
        
        self._params.append(vrrp_block)
        return vrrp_block

    def remove_vrrp_instance(self, instance_name: str) -> bool:
        """
        Remove VRRP instance
        
        Args:
            instance_name (str): Name of the instance to delete
            
        Returns:
            bool: Whether deletion was successful
        """
        for i, param in enumerate(self._params):
            if isinstance(param, KeepAlivedConfigBlock) and \
               param.name == f"vrrp_instance {instance_name}":
                del self._params[i]
                return True
        return False

    def to_str(self, indent_level=0, indent_size=None):
        if indent_size is None:
            indent_size = KeepAlivedConfigConstants.INDENT_SIZE
            
        Str = ""
        if self.__get_generic_comments__():
            Str = (
                "\n".join(
                    [
                        f"{' ' * indent_size * indent_level}{str(comment)}"
                        for comment in self.__get_generic_comments__()
                    ]
                )
                + "\n"
            )
            
        Str += f"{' ' * indent_size * indent_level}{self._name} {{\n"
        for param in self._params:
            if isinstance(param, KeepAlivedConfigBlock):
                Str += param.to_str(indent_level + 1, indent_size) + "\n"
            elif isinstance(param, KeepAlivedConfigParam):
                # Temporarily override indent size for this parameter
                original_indent_size = KeepAlivedConfigConstants.INDENT_SIZE
                KeepAlivedConfigConstants.INDENT_SIZE = indent_size
                try:
                    Str += param.to_str(indent_level + 1) + "\n"
                finally:
                    # Restore original indent size
                    KeepAlivedConfigConstants.INDENT_SIZE = original_indent_size
        Str += f"{' ' * indent_size * indent_level}}}{self.__get_inline_comment__() if self.__get_inline_comment__() else ''}"
        return Str

    def format_config(self, indent_level=0):
        """
        Format configuration block, unify indentation and layout
        
        Args:
            indent_level (int): Indentation level, default is 0
            
        Returns:
            str: Formatted configuration string
        """
        return self.to_str(indent_level)

    def __str__(self):
        return self.to_str()
