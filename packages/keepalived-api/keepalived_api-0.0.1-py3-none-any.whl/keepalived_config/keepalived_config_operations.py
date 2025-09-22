import os
import copy
import json
from collections import deque

from keepalived_config.keepalived_config_constants import KeepAlivedConfigConstants
from keepalived_config.keepalived_config_param import KeepAlivedConfigParam
from keepalived_config.keepalived_config_block import KeepAlivedConfigBlock
from keepalived_config.keepalived_config_comment import (
    KeepAlivedConfigComment,
    KeepAlivedConfigCommentTypes,
)


class KeepAlivedConfigOperations:
    
    def to_dict(self, config_params) -> dict:
        """
        Convert configuration to dictionary format
        
        Returns:
            dict: Dictionary representation of configuration
        """
        def _param_to_dict(param):
            if isinstance(param, KeepAlivedConfigBlock):
                result = {
                    "type": "block",
                    "name": param.name,
                    "params": [_param_to_dict(p) for p in param.params]
                }
                if param.comments:
                    result["comments"] = [str(c) for c in param.comments]
                return result
            else:
                result = {
                    "type": "param",
                    "name": param.name,
                    "value": param.value
                }
                if param.comments:
                    result["comments"] = [str(c) for c in param.comments]
                return result
        
        return {
            "params": [_param_to_dict(param) for param in config_params]
        }

    def to_json(self, config_params) -> str:
        """
        Export configuration as JSON format
        
        Returns:
            str: Configuration string in JSON format
        """
        return json.dumps(self.to_dict(config_params), indent=2, ensure_ascii=False)

    def merge(self, config_params, other_config_params) -> list:
        """
        Merge another configuration into the current configuration
        
        Args:
            other_config_params: Parameters from another configuration to merge
            
        Returns:
            list: Merged parameters list
        """
        merged_params = copy.deepcopy(config_params)
        
        def _merge_recursive(target_items, source_items):
            for source_item in source_items:
                # Check if a block with the same name already exists
                existing_item = None
                for i, target_item in enumerate(target_items):
                    if (hasattr(target_item, 'name') and hasattr(source_item, 'name') and
                        target_item.name == source_item.name and
                        type(target_item) == type(source_item)):
                        existing_item = target_item
                        existing_index = i
                        break
                
                if existing_item and isinstance(existing_item, KeepAlivedConfigBlock):
                    # If it's a block and already exists, merge its parameters
                    _merge_recursive(existing_item.params, source_item.params)
                else:
                    # Otherwise add new item
                    target_items.append(copy.deepcopy(source_item))
        
        _merge_recursive(merged_params, other_config_params)
        return merged_params

    def apply_template_params(self, config_params, param_mapping: dict) -> list:
        """
        Apply parameters to a template-based configuration by replacing placeholders
        
        Args:
            param_mapping (dict): Dictionary mapping placeholder names to actual values
            
        Returns:
            list: Updated parameters list
            
        Raises:
            TypeError: If param_mapping is not a dictionary
        """
        if not isinstance(param_mapping, dict):
            raise TypeError("param_mapping must be a dictionary")
            
        def _replace_placeholders(items):
            for item in items:
                if isinstance(item, KeepAlivedConfigParam):
                    # Replace parameter values
                    if item.value in param_mapping:
                        item.value = str(param_mapping[item.value])
                elif isinstance(item, KeepAlivedConfigBlock):
                    # Replace block names (for cases like virtual_server IP PORT)
                    for placeholder, value in param_mapping.items():
                        if placeholder in item.name:
                            item.name = item.name.replace(placeholder, str(value))
                    
                    # Process parameters within the block
                    for param in item.params:
                        if isinstance(param, KeepAlivedConfigParam):
                            # Replace parameter values
                            if param.value in param_mapping:
                                param.value = str(param_mapping[param.value])
                            # Special handling for virtual_ipaddress with placeholder
                            elif param.value == "" and param.name == "":
                                # This handles the case where we have an empty parameter with placeholder content
                                if "VIRTUAL_IP_ADDRESS" in param_mapping:
                                    param.value = str(param_mapping["VIRTUAL_IP_ADDRESS"])
                        elif isinstance(param, KeepAlivedConfigBlock):
                            # Recursively process nested blocks
                            _replace_placeholders([param])
                # Recursively process nested parameters
                if hasattr(item, 'params'):
                    _replace_placeholders(item.params)
        
        _replace_placeholders(config_params)
        return config_params

    def format_config(self, config_params) -> str:
        """
        Format configuration, unify indentation and layout
        
        Returns:
            str: Formatted configuration string
        """
        formatted_lines = []
        for item in config_params:
            formatted_lines.append(item.to_str())
        return "\n".join(formatted_lines)

    def clone(self, config_params) -> list:
        """
        Clone the current configuration object
        
        Returns:
            list: Deep copy of the configuration parameters
        """
        return copy.deepcopy(config_params)

    def validate(self, config_params) -> list:
        """
        Validate if configuration conforms to keepalived syntax specifications
        
        Returns:
            list: List of error messages
        """
        errors = []
        
        def _validate_recursive(items, path=""):
            for item in items:
                current_path = f"{path}.{item.name}" if path else item.name
                
                # Check if parameter name is empty (except for empty lines)
                if not hasattr(item, 'name'):
                    continue
                    
                if not item.name and (item.value or hasattr(item, 'params')):
                    errors.append(f"Invalid empty parameter at {current_path}")
                    continue
                    
                # Check VRRP instance configuration
                if isinstance(item, KeepAlivedConfigBlock) and item.name.startswith("vrrp_instance"):
                    # Check required parameters
                    required_params = {"state", "interface", "virtual_router_id", "priority"}
                    existing_params = {param.name for param in item.params if hasattr(param, 'name') and param.name}
                    
                    missing_params = required_params - existing_params
                    for missing in missing_params:
                        errors.append(f"Missing required parameter '{missing}' in {current_path}")
                        
                    # Check state parameter value
                    for param in item.params:
                        if param.name == "state" and param.value not in ["MASTER", "BACKUP"]:
                            errors.append(f"Invalid state value '{param.value}' in {current_path}, expected MASTER or BACKUP")
                            
                        # Check priority parameter value
                        if param.name == "priority":
                            try:
                                priority = int(param.value)
                                if priority < 1 or priority > 255:
                                    errors.append(f"Invalid priority value '{param.value}' in {current_path}, expected 1-255")
                            except ValueError:
                                errors.append(f"Invalid priority value '{param.value}' in {current_path}, expected integer")
                
                # Recursively validate nested parameters
                if hasattr(item, 'params'):
                    _validate_recursive(item.params, current_path)
        
        _validate_recursive(config_params)
        return errors

    def filter_params(self, config_params, param_type=None, name_pattern=None):
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

    def traverse(self, config_params, visit_func, order="dfs"):
        """
        Traverse configuration items
        
        Args:
            visit_func (function): Visit function that accepts one parameter (configuration item)
            order (str): Traversal order, "dfs" means depth-first, "bfs" means breadth-first
        """
        if order == "dfs":
            def _dfs_recursive(items):
                for item in items:
                    visit_func(item)
                    if hasattr(item, 'params'):
                        _dfs_recursive(item.params)
            
            _dfs_recursive(config_params)
        elif order == "bfs":
            queue = deque(config_params)
            while queue:
                item = queue.popleft()
                visit_func(item)
                if hasattr(item, 'params'):
                    queue.extend(item.params)

    def xpath(self, config_params, path: str) -> list:
        """
        Find parameters using XPath-like expressions
        
        Args:
            path (str): XPath-like expression to search for
            
        Returns:
            list: List of matching parameters
        """
        parts = path.strip("/").split("/")
        results = []
        
        def _search_recursive(items, part_index=0):
            if part_index >= len(parts):
                return items
            
            name_pattern = parts[part_index]
            next_results = []
            
            for item in items:
                # Exact match or pattern match
                if hasattr(item, 'name'):
                    # Support for exact matching with =
                    if name_pattern.startswith("="):
                        exact_name = name_pattern[1:]
                        if item.name == exact_name:
                            if part_index == len(parts) - 1:
                                next_results.append(item)
                            else:
                                if hasattr(item, 'params'):
                                    next_results.extend(_search_recursive(item.params, part_index + 1))
                    # Support for pattern matching (original behavior)
                    elif name_pattern in item.name:
                        if part_index == len(parts) - 1:
                            next_results.append(item)
                        else:
                            if hasattr(item, 'params'):
                                next_results.extend(_search_recursive(item.params, part_index + 1))
                
                # Recursively search nested parameters
                if hasattr(item, 'params'):
                    if part_index == len(parts) - 1 and "*" in name_pattern:
                        next_results.extend([p for p in item.params if not hasattr(p, 'name') or p.name != ""])
                    elif part_index < len(parts) - 1:
                        next_results.extend(_search_recursive(item.params, part_index))
            
            return next_results
        
        return _search_recursive(config_params)

    def find_param(self, config_params, path: str):
        """
        Method to find configuration items by path
        
        Args:
            path (str): Configuration item path, such as "global_defs.notification_email"
            
        Returns:
            KeepAlivedConfigParam | KeepAlivedConfigBlock | None: Found configuration item or None
        """
        if not path:
            return None
            
        parts = path.split('.')
        current_items = config_params
        
        for i, part in enumerate(parts):
            found = None
            # Search in current level
            for item in current_items:
                if hasattr(item, 'name') and item.name.startswith(part):
                    found = item
                    break
            
            if found is None:
                return None
                
            # If it's the last part, return directly
            if i == len(parts) - 1:
                return found
                
            # If it's not the last part, but the found item is not a block, the path is invalid
            if not hasattr(found, 'params'):
                return None
                
            # Continue searching in the next level
            current_items = found.params
            
        return None

    def set_param(self, config_params, path: str, value: str) -> list:
        """
        Set a single parameter value by path
        
        Args:
            path (str): Path to the parameter (e.g., "global_defs.router_id")
            value (str): New value for the parameter
            
        Returns:
            list: Updated configuration parameters
        """
        item = self.find_param(config_params, path)
        if isinstance(item, KeepAlivedConfigParam):
            item.value = str(value)
        return config_params

    def set_multiple_params(self, config_params, param_updates: dict) -> list:
        """
        Set multiple parameters at once using a dictionary
        
        Args:
            param_updates (dict): Dictionary with parameter paths as keys and values
            
        Returns:
            list: Updated configuration parameters
            
        Example:
            config.set_multiple_params({
                "global_defs.notification_email_from": "new_email@example.com",
                "vrrp_instance VI_1.priority": "150"
            })
        """
        for path, value in param_updates.items():
            self.set_param(config_params, path, value)
        return config_params

    def get_param(self, config_params, path: str) -> KeepAlivedConfigParam | None:
        """
        Get a single parameter by path
        
        Args:
            path (str): Path to the parameter (e.g., "global_defs.router_id")
            
        Returns:
            KeepAlivedConfigParam | None: The parameter object or None if not found
        """
        item = self.find_param(config_params, path)
        if isinstance(item, KeepAlivedConfigParam):
            return item
        return None

    def has_param(self, config_params, path: str) -> bool:
        """
        Check if a parameter exists at the given path
        
        Args:
            path (str): Path to the parameter (e.g., "global_defs.router_id")
            
        Returns:
            bool: True if parameter exists, False otherwise
        """
        return self.get_param(config_params, path) is not None

    def remove_param(self, config_params, path: str) -> bool:
        """
        Remove a parameter by path
        
        Args:
            path (str): Path to the parameter to remove
            
        Returns:
            bool: True if parameter was removed, False if not found
        """
        parts = path.split('.')
        if len(parts) == 0:
            return False
            
        # Navigate to the parent of the target parameter
        current_items = config_params
        parent_items = None
        target_name = parts[-1]
        
        # Navigate through the path
        for part in parts[:-1]:
            found = None
            for item in current_items:
                if hasattr(item, 'name') and item.name == part:
                    found = item
                    break
            if found is None or not hasattr(found, 'params'):
                return False
            parent_items = current_items
            current_items = found.params
            
        # Find and remove the target parameter
        for i, item in enumerate(current_items):
            if hasattr(item, 'name') and item.name == target_name:
                del current_items[i]
                return True
                
        return False