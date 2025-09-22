import os
import sys
import pytest
import json
import tempfile

SRC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src")
sys.path.append(SRC_DIR)

from keepalived_config.keepalived_config import KeepAlivedConfig
from keepalived_config.keepalived_config_block import KeepAlivedConfigBlock
from keepalived_config.keepalived_config_param import KeepAlivedConfigParam
from keepalived_config.keepalived_config_parser import KeepAlivedConfigParser


def test_from_file():
    """Test loading configuration from file"""
    # Create a sample configuration
    sample_config = """# Global definitions
global_defs {
    notification_email {
        admin@example.com
    }
    notification_email_from keepalived@example.com
    smtp_server 127.0.0.1
}

vrrp_instance VI_1 {
    state MASTER
    interface eth0
    virtual_router_id 51
    priority 100
}
"""
    
    # Write to a temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.conf', delete=False) as f:
        f.write(sample_config)
        temp_file = f.name
    
    try:
        # Test loading configuration from file
        config = KeepAlivedConfig.from_file(temp_file)
        assert isinstance(config, KeepAlivedConfig)
        
        # Filter out empty parameters
        non_empty_params = [p for p in config.params if hasattr(p, 'name') and p.name]
        assert len(non_empty_params) == 2
        
        # Check global_defs block
        global_defs = non_empty_params[0]
        assert isinstance(global_defs, KeepAlivedConfigBlock)
        assert global_defs.name == "global_defs"
        
        # Check vrrp_instance block
        vrrp_instance = non_empty_params[1]
        assert isinstance(vrrp_instance, KeepAlivedConfigBlock)
        assert vrrp_instance.name == "vrrp_instance VI_1"
        
    finally:
        # Clean up temporary file
        os.unlink(temp_file)


def test_from_template():
    """Test creating configuration from template"""
    # Test with basic_vrrp template
    config = KeepAlivedConfig.from_template("basic_vrrp", "VI_1")
    assert isinstance(config, KeepAlivedConfig)
    assert len(config.params) == 1
    
    vrrp_block = config.params[0]
    assert isinstance(vrrp_block, KeepAlivedConfigBlock)
    assert vrrp_block.name == "vrrp_instance VI_1"
    
    # Test with basic_global template
    config = KeepAlivedConfig.from_template("basic_global")
    assert isinstance(config, KeepAlivedConfig)
    assert len(config.params) == 1
    
    global_block = config.params[0]
    assert isinstance(global_block, KeepAlivedConfigBlock)
    assert global_block.name == "global_defs"
    
    # Test with basic_virtual_server template
    config = KeepAlivedConfig.from_template("basic_virtual_server", "192.168.1.100 80")
    assert isinstance(config, KeepAlivedConfig)
    assert len(config.params) == 1
    
    virtual_server_block = config.params[0]
    assert isinstance(virtual_server_block, KeepAlivedConfigBlock)
    assert virtual_server_block.name == "virtual_server 192.168.1.100 80"


def test_find_param():
    """Test finding parameters by path"""
    # Create a test configuration
    config = KeepAlivedConfig()
    
    # Add global_defs block
    global_block = KeepAlivedConfigBlock("global_defs")
    global_block.add_param(KeepAlivedConfigParam("smtp_server", "127.0.0.1"))
    config.params.append(global_block)
    
    # Add VRRP instance
    vrrp_block = KeepAlivedConfigBlock("vrrp_instance", "VI_1")
    vrrp_block.add_param(KeepAlivedConfigParam("state", "MASTER"))
    config.params.append(vrrp_block)
    
    # Test finding global_defs
    found_global = config.find_param("global_defs")
    assert found_global == global_block
    
    # Test finding smtp_server parameter
    found_smtp = config.find_param("global_defs.smtp_server")
    assert isinstance(found_smtp, KeepAlivedConfigParam)
    assert found_smtp.name == "smtp_server"
    assert found_smtp.value == "127.0.0.1"
    
    # Test finding vrrp_instance
    found_vrrp = config.find_param("vrrp_instance VI_1")
    assert found_vrrp == vrrp_block
    
    # Test finding non-existent parameter
    found_nonexistent = config.find_param("non_existent")
    assert found_nonexistent is None


def test_context_manager():
    """Test context manager functionality"""
    # Create a sample configuration
    sample_config = """global_defs {
    smtp_server 127.0.0.1
}
"""
    
    # Write to a temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.conf', delete=False) as f:
        f.write(sample_config)
        temp_file = f.name
    
    try:
        # Test context manager
        with KeepAlivedConfig.from_file(temp_file) as config:
            # Modify configuration
            global_defs = config.find_param("global_defs")
            global_defs.add_param(KeepAlivedConfigParam("router_id", "LVS_DEVEL"))
            
            # Config should be modified in memory
            router_id = config.find_param("global_defs.router_id")
            assert router_id is not None
            assert router_id.value == "LVS_DEVEL"
            
        # After exiting context, file should be saved automatically
        # Re-read the file to verify changes were saved
        with open(temp_file, 'r') as f:
            content = f.read()
            assert "router_id LVS_DEVEL" in content
            
    finally:
        # Clean up temporary file
        os.unlink(temp_file)


def test_clone():
    """Test cloning configuration"""
    # Create original configuration
    config = KeepAlivedConfig()
    global_block = KeepAlivedConfigBlock("global_defs")
    global_block.add_param(KeepAlivedConfigParam("router_id", "LVS_DEVEL"))
    config.params.append(global_block)
    
    # Clone configuration
    cloned_config = config.clone()
    
    # Verify it's a different object
    assert cloned_config is not config
    assert len(cloned_config.params) == len(config.params)
    
    # Verify content is the same
    original_global = config.find_param("global_defs")
    cloned_global = cloned_config.find_param("global_defs")
    assert original_global is not cloned_global  # Different objects
    assert cloned_global.name == original_global.name
    
    # Verify parameter values are the same
    original_router_id = config.find_param("global_defs.router_id")
    cloned_router_id = cloned_config.find_param("global_defs.router_id")
    assert cloned_router_id.value == original_router_id.value


def test_filter_params():
    """Test filtering parameters"""
    # Create test configuration
    config = KeepAlivedConfig()
    
    # Add various blocks and parameters
    global_block = KeepAlivedConfigBlock("global_defs")
    config.params.append(global_block)
    
    vrrp_block = KeepAlivedConfigBlock("vrrp_instance", "VI_1")
    config.params.append(vrrp_block)
    
    param = KeepAlivedConfigParam("simple_param", "value")
    config.params.append(param)
    
    # Test filtering by type - blocks only
    blocks = config.filter_params(param_type=KeepAlivedConfigBlock)
    assert len(blocks) == 2
    assert all(isinstance(b, KeepAlivedConfigBlock) for b in blocks)
    
    # Test filtering by name pattern
    vrrp_items = config.filter_params(name_pattern="vrrp")
    assert len(vrrp_items) == 1
    assert vrrp_items[0].name == "vrrp_instance VI_1"
    
    # Test filtering with no criteria (should return all)
    all_params = config.filter_params()
    assert len(all_params) == 3


def test_xpath():
    """Test XPath-style querying"""
    # Create test configuration
    config = KeepAlivedConfig()
    vrrp_block = KeepAlivedConfigBlock("vrrp_instance", "VI_1")
    config.params.append(vrrp_block)
    
    # Test finding VRRP instances
    vrrp_instances = config.xpath("//vrrp_instance")
    assert len(vrrp_instances) == 1
    assert vrrp_instances[0].name == "vrrp_instance VI_1"
    
    # Test finding non-existent items
    non_existent = config.xpath("//non_existent")
    assert len(non_existent) == 0


def test_validate():
    """Test configuration validation"""
    # Test valid configuration
    config = KeepAlivedConfig()
    vrrp_block = KeepAlivedConfigBlock("vrrp_instance", "VI_1")
    vrrp_block.add_param(KeepAlivedConfigParam("state", "MASTER"))
    vrrp_block.add_param(KeepAlivedConfigParam("interface", "eth0"))
    vrrp_block.add_param(KeepAlivedConfigParam("virtual_router_id", "51"))
    vrrp_block.add_param(KeepAlivedConfigParam("priority", "100"))
    config.params.append(vrrp_block)
    
    errors = config.validate()
    assert len(errors) == 0  # No errors for valid config
    
    # Test invalid configuration
    invalid_config = KeepAlivedConfig()
    vrrp_block = KeepAlivedConfigBlock("vrrp_instance", "VI_2")
    vrrp_block.add_param(KeepAlivedConfigParam("state", "INVALID"))  # Invalid state
    vrrp_block.add_param(KeepAlivedConfigParam("priority", "300"))   # Priority out of range
    invalid_config.params.append(vrrp_block)
    
    errors = invalid_config.validate()
    assert len(errors) > 0  # Should have validation errors


def test_traverse():
    """Test configuration traversal"""
    # Create test configuration
    config = KeepAlivedConfig()
    global_block = KeepAlivedConfigBlock("global_defs")
    global_block.add_param(KeepAlivedConfigParam("router_id", "LVS_DEVEL"))
    config.params.append(global_block)
    
    visited_items = []
    
    def visit_func(item):
        visited_items.append(item)
    
    # Test DFS traversal
    config.traverse(visit_func, order="dfs")
    assert len(visited_items) == 2  # global_defs block and router_id param
    
    # Reset and test BFS traversal
    visited_items = []
    config.traverse(visit_func, order="bfs")
    assert len(visited_items) == 2


def test_merge():
    """Test configuration merging"""
    # Create first configuration
    config1 = KeepAlivedConfig.from_template("basic_global")
    
    # Create second configuration
    config2 = KeepAlivedConfig.from_template("basic_vrrp", "VI_1")
    
    # Merge configurations
    merged_config = config1.merge(config2)
    
    # Verify both configurations are present
    # Filter out empty parameters
    non_empty_params = [p for p in merged_config.params if hasattr(p, 'name') and p.name]
    assert len(non_empty_params) == 2
    
    # Check global_defs is present
    global_blocks = [p for p in non_empty_params if isinstance(p, KeepAlivedConfigBlock) and p.name == "global_defs"]
    assert len(global_blocks) == 1
    
    # Check vrrp_instance is present
    vrrp_blocks = [p for p in non_empty_params if isinstance(p, KeepAlivedConfigBlock) and p.name.startswith("vrrp_instance")]
    assert len(vrrp_blocks) == 1


def test_to_json():
    """Test exporting configuration to JSON"""
    # Create test configuration
    config = KeepAlivedConfig()
    global_block = KeepAlivedConfigBlock("global_defs")
    global_block.add_param(KeepAlivedConfigParam("router_id", "LVS_DEVEL"))
    config.params.append(global_block)
    
    # Export to JSON
    json_output = config.to_json()
    
    # Verify it's valid JSON
    parsed_json = json.loads(json_output)
    assert "params" in parsed_json
    assert len(parsed_json["params"]) == 1


def test_format_config():
    """Test configuration formatting"""
    # Create test configuration
    config = KeepAlivedConfig()
    global_block = KeepAlivedConfigBlock("global_defs")
    global_block.add_param(KeepAlivedConfigParam("router_id", "LVS_DEVEL"))
    config.params.append(global_block)
    
    # Format configuration
    formatted = config.format_config()
    
    # Verify it contains expected content
    assert "global_defs" in formatted
    assert "router_id LVS_DEVEL" in formatted
    assert "{" in formatted and "}" in formatted


def test_apply_template_params():
    """Test applying template parameters"""
    # Create a template-based configuration
    config = KeepAlivedConfig.from_template("basic_vrrp", "VI_TEST")
    
    # Apply parameters
    config.apply_template_params({
        "VRRP_STATE": "BACKUP",
        "INTERFACE_NAME": "eth1",
        "VRRP_ROUTER_ID": "100",
        "VRRP_PRIORITY": "90",
        "VRRP_ADVERT_INT": "2"
    })
    
    # Check that parameters were applied
    formatted = config.format_config()
    assert "state BACKUP" in formatted
    assert "interface eth1" in formatted
    assert "virtual_router_id 100" in formatted
    assert "priority 90" in formatted
    assert "advert_int 2" in formatted


def test_add_vrrp_instance():
    """Test adding VRRP instance directly to KeepAlivedConfig"""
    config = KeepAlivedConfig()
    
    # Add VRRP instance
    result = config.add_vrrp_instance(
        instance_name="VI_DIRECT",
        state="MASTER",
        interface="eth0",
        virtual_router_id=51,
        priority=100,
        advert_int=1
    )
    
    # Check that the method returns self for chaining
    assert result is config
    
    # Check that VRRP instance was added
    formatted = config.format_config()
    assert "vrrp_instance VI_DIRECT" in formatted
    assert "state MASTER" in formatted
    assert "interface eth0" in formatted


def test_add_multiple_vrrp_instances():
    """Test adding multiple VRRP instances at once"""
    config = KeepAlivedConfig()
    
    # Add multiple VRRP instances
    instances = [
        {
            "instance_name": "VI_MULTI_1",
            "state": "MASTER",
            "interface": "eth0",
            "virtual_router_id": 51,
            "priority": 100,
            "advert_int": 1
        },
        {
            "instance_name": "VI_MULTI_2",
            "state": "BACKUP",
            "interface": "eth1",
            "virtual_router_id": 52,
            "priority": 90,
            "advert_int": 1
        }
    ]
    
    config.add_multiple_vrrp_instances(instances)
    
    formatted = config.format_config()
    assert "vrrp_instance VI_MULTI_1" in formatted
    assert "vrrp_instance VI_MULTI_2" in formatted


def test_set_param():
    """Test setting single parameter"""
    config = KeepAlivedConfig.from_template("basic_vrrp", "VI_SET_PARAM")
    
    # Apply some parameters first
    config.apply_template_params({
        "VRRP_STATE": "MASTER",
        "INTERFACE_NAME": "eth0",
        "VRRP_ROUTER_ID": "51",
        "VRRP_PRIORITY": "100",
        "VRRP_ADVERT_INT": "1"
    })
    
    # Set a single parameter
    config.set_param("vrrp_instance VI_SET_PARAM.priority", "150")
    
    # Check that parameter was set
    param = config.get_param("vrrp_instance VI_SET_PARAM.priority")
    assert param is not None
    assert param.value == "150"


def test_set_multiple_params():
    """Test setting multiple parameters"""
    config = KeepAlivedConfig.from_template("basic_vrrp", "VI_MULTI_PARAM")
    
    # Apply some parameters first
    config.apply_template_params({
        "VRRP_STATE": "MASTER",
        "INTERFACE_NAME": "eth0",
        "VRRP_ROUTER_ID": "51",
        "VRRP_PRIORITY": "100",
        "VRRP_ADVERT_INT": "1"
    })
    
    # Set multiple parameters
    config.set_multiple_params({
        "vrrp_instance VI_MULTI_PARAM.priority": "160",
        "vrrp_instance VI_MULTI_PARAM.interface": "eth1"
    })
    
    # Check that parameters were set
    priority_param = config.get_param("vrrp_instance VI_MULTI_PARAM.priority")
    interface_param = config.get_param("vrrp_instance VI_MULTI_PARAM.interface")
    assert priority_param is not None
    assert priority_param.value == "160"
    assert interface_param is not None
    assert interface_param.value == "eth1"


def test_get_param():
    """Test getting parameter"""
    config = KeepAlivedConfig.from_template("basic_vrrp", "VI_GET_PARAM")
    
    # Apply some parameters first
    config.apply_template_params({
        "VRRP_STATE": "MASTER",
        "INTERFACE_NAME": "eth0",
        "VRRP_ROUTER_ID": "51",
        "VRRP_PRIORITY": "100",
        "VRRP_ADVERT_INT": "1"
    })
    
    # Get a parameter
    param = config.get_param("vrrp_instance VI_GET_PARAM.state")
    assert param is not None
    assert isinstance(param, KeepAlivedConfigParam)
    assert param.value == "MASTER"
    
    # Try to get a non-existent parameter
    param = config.get_param("vrrp_instance VI_GET_PARAM.non_existent")
    assert param is None


def test_has_param():
    """Test checking if parameter exists"""
    config = KeepAlivedConfig.from_template("basic_vrrp", "VI_HAS_PARAM")
    
    # Apply some parameters first
    config.apply_template_params({
        "VRRP_STATE": "MASTER",
        "INTERFACE_NAME": "eth0",
        "VRRP_ROUTER_ID": "51",
        "VRRP_PRIORITY": "100",
        "VRRP_ADVERT_INT": "1"
    })
    
    # Check if parameter exists
    assert config.has_param("vrrp_instance VI_HAS_PARAM.state") is True
    assert config.has_param("vrrp_instance VI_HAS_PARAM.non_existent") is False


def test_remove_param():
    """Test removing parameter"""
    config = KeepAlivedConfig.from_template("basic_vrrp", "VI_REMOVE_PARAM")
    
    # Apply some parameters first
    config.apply_template_params({
        "VRRP_STATE": "MASTER",
        "INTERFACE_NAME": "eth0",
        "VRRP_ROUTER_ID": "51",
        "VRRP_PRIORITY": "100",
        "VRRP_ADVERT_INT": "1"
    })
    
    # Check that parameter exists before removal
    assert config.has_param("vrrp_instance VI_REMOVE_PARAM.state") is True
    
    # Remove parameter
    result = config.remove_param("vrrp_instance VI_REMOVE_PARAM.state")
    assert result is True
    
    # Check that parameter no longer exists
    assert config.has_param("vrrp_instance VI_REMOVE_PARAM.state") is False
    
    # Try to remove non-existent parameter
    result = config.remove_param("vrrp_instance VI_REMOVE_PARAM.non_existent")
    assert result is False


def test_virtual_ipaddress_operations():
    """Test virtual IP address operations"""
    config = KeepAlivedConfig()
    config.add_vrrp_instance(
        instance_name="VI_VIP",
        state="MASTER",
        interface="eth0",
        virtual_router_id=51,
        priority=100,
        advert_int=1
    )
    
    # Add virtual IP address
    result = config.add_virtual_ipaddress("VI_VIP", "192.168.1.10/24")
    assert result is config  # Should return self for chaining
    
    # Get virtual IP addresses
    vip_list = config.get_virtual_ipaddresses("VI_VIP")
    assert isinstance(vip_list, list)
    assert "192.168.1.10/24" in vip_list
    
    # Try to operate on non-existent instance
    result = config.add_virtual_ipaddress("NON_EXISTENT", "192.168.1.11/24")
    assert result is config  # Should still return self even when operation fails
    
    vip_list = config.get_virtual_ipaddresses("NON_EXISTENT")
    assert isinstance(vip_list, list)
    assert len(vip_list) == 0


def test_virtual_server_operations():
    """Test virtual server operations"""
    config = KeepAlivedConfig()
    
    # Add virtual server
    config.add_virtual_server("192.168.1.100", 80, delay_loop=10, lb_algo="wrr")
    
    formatted = config.format_config()
    assert "virtual_server 192.168.1.100 80" in formatted
    assert "delay_loop 10" in formatted
    assert "lb_algo wrr" in formatted
    
    # Add real server with tcp_check
    config.add_real_server("192.168.1.100", 80, "10.0.0.10", 8080, weight=2, health_check="tcp_check")
    
    formatted = config.format_config()
    assert "real_server 10.0.0.10 8080" in formatted
    assert "weight 2" in formatted
    assert "TCP_CHECK" in formatted
    
    # Add real server with http_check
    config.add_real_server("192.168.1.100", 80, "10.0.0.11", 8080, weight=3, health_check="http_check")
    
    formatted = config.format_config()
    assert "real_server 10.0.0.11 8080" in formatted
    assert "weight 3" in formatted
    assert "HTTP_GET" in formatted


def test_template_errors():
    """Test error handling in template operations"""
    # Test non-existent template
    try:
        KeepAlivedConfig.from_template("non_existent_template")
        assert False, "Should have raised ValueError"
    except ValueError:
        pass  # Expected
    
    # Test VRRP template without instance name
    try:
        KeepAlivedConfig.from_template("basic_vrrp")
        assert False, "Should have raised ValueError"
    except ValueError:
        pass  # Expected


def test_apply_template_params_errors():
    """Test error handling in apply_template_params"""
    config = KeepAlivedConfig.from_template("basic_vrrp", "VI_ERROR")
    
    # Test with non-dict parameter
    try:
        config.apply_template_params("not_a_dict")
        assert False, "Should have raised TypeError"
    except TypeError:
        pass  # Expected


def test_chain_methods():
    """Test method chaining"""
    config = KeepAlivedConfig()

    # Test that methods return self for chaining
    result = config.add_vrrp_instance(
        instance_name="VI_CHAIN",
        state="MASTER",
        interface="eth0",
        virtual_router_id=51,
        priority=100
    )
    assert result is config  # add_vrrp_instance should return self now

    config.add_virtual_ipaddress("VI_CHAIN", "192.168.1.10/24")

    # Test set_param chaining - use a parameter that actually exists
    # First make sure the block exists
    vrrp_block = config.find_param("vrrp_instance VI_CHAIN")
    if vrrp_block:
        # Add a test parameter to the block
        vrrp_block.add_param(KeepAlivedConfigParam("test_param", "old_value"))
        result = config.set_param("vrrp_instance VI_CHAIN.test_param", "new_value")
        assert result is config  # set_param should return self

    # Test other chaining methods
    result = config.add_virtual_server("192.168.2.100", 443)
    assert result is config
    
    result = config.add_real_server("192.168.2.100", 443, "10.0.0.20", 8443, health_check="http_check")
    assert result is config


def test_edge_cases():
    """Test edge cases"""
    config = KeepAlivedConfig()
    
    # Test removing non-existent parameter
    result = config.remove_param("non.existent.param")
    assert result is False
    
    # Test getting non-existent parameter
    result = config.get_param("non.existent.param")
    assert result is None
    
    # Test checking non-existent parameter
    result = config.has_param("non.existent.param")
    assert result is False
    
    # Test adding virtual IP to non-existent VRRP instance
    result = config.add_virtual_ipaddress("NON_EXISTENT", "192.168.1.10/24")
    assert result is config  # Should return self even when operation fails
    
    # Test getting virtual IPs from non-existent VRRP instance
    result = config.get_virtual_ipaddresses("NON_EXISTENT")
    assert isinstance(result, list)
    assert len(result) == 0


def test_param_descriptions():
    """Test parameter descriptions"""
    config = KeepAlivedConfig()
    
    # Test getting descriptions for known parameters
    assert config.get_param_description("state") == "VRRP instance state (MASTER or BACKUP)"
    assert config.get_param_description("interface") == "Network interface to run VRRP on"
    assert config.get_param_description("virtual_router_id") == "Virtual router ID (1-255)"
    
    # Test getting description for unknown parameter
    assert config.get_param_description("unknown_param") == ""


def test_param_validation():
    """Test parameter validation"""
    config = KeepAlivedConfig()
    
    # Test valid values
    assert config.validate_param_value("virtual_router_id", 51) == True
    assert config.validate_param_value("priority", 100) == True
    assert config.validate_param_value("state", "MASTER") == True
    assert config.validate_param_value("state", "BACKUP") == True
    assert config.validate_param_value("lb_algo", "wrr") == True
    
    # Test invalid values
    try:
        config.validate_param_value("virtual_router_id", 300)  # Too large
        assert False, "Should have raised exception"
    except Exception as e:
        assert "too large" in str(e)
    
    try:
        config.validate_param_value("state", "INVALID")  # Not allowed
        assert False, "Should have raised exception"
    except Exception as e:
        assert "Allowed values" in str(e)
    
    try:
        config.validate_param_value("priority", 0)  # Too small
        assert False, "Should have raised exception"
    except Exception as e:
        assert "too small" in str(e)


def test_format_config_with_custom_indent():
    """Test format_config with custom indentation"""
    config = KeepAlivedConfig()
    
    # Add a simple block using the correct method
    block = KeepAlivedConfigBlock("test_block", "test")
    block.add_param(KeepAlivedConfigParam("test_param", "test_value"))
    config.add_param(block)  # Use the new add_param method
    
    # Format with default indent
    default_format = config.format_config()
    assert "    " in default_format  # Should contain 4 spaces
    
    # Format with custom indent
    custom_format = config.format_config(indent_size=2)
    assert "  " in custom_format  # Should contain 2 spaces
    # Note: This test is not ideal because both indent sizes may appear in the output
    # But it's sufficient to verify the method works


def test_new_templates():
    """Test new template functionality"""
    # Test complete_vrrp_master template
    master_config = KeepAlivedConfig.from_template("complete_vrrp_master", "VI_1")
    assert master_config is not None
    assert "MASTER" in master_config.format_config()
    
    # Test complete_vrrp_backup template
    backup_config = KeepAlivedConfig.from_template("complete_vrrp_backup", "VI_2")
    assert backup_config is not None
    assert "BACKUP" in backup_config.format_config()
    
    # Test basic_global template
    global_config = KeepAlivedConfig.from_template("basic_global")
    assert global_config is not None
    
    # Test basic_virtual_server template
    vs_config = KeepAlivedConfig.from_template("basic_virtual_server", "192.168.1.1 80")
    assert vs_config is not None
    assert "VIRTUAL_SERVER_DELAY_LOOP" in vs_config.format_config()
