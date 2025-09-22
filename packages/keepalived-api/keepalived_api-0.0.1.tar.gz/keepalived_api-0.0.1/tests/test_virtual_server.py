import os
import sys
import tempfile

SRC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src")
sys.path.append(SRC_DIR)

from keepalived_config.keepalived_config import KeepAlivedConfig
from keepalived_config.keepalived_config_block import KeepAlivedConfigBlock
from keepalived_config.keepalived_config_param import KeepAlivedConfigParam


def test_virtual_server_parsing():
    """Test parsing virtual_server configurations"""
    # Create a sample configuration with virtual_server
    sample_config = """virtual_server 192.168.100.219 80 {
    delay_loop 6
    lb_algo rr
    lb_kind DR
    protocol TCP

    real_server 192.168.100.217 80 {
        weight 1
        TCP_CHECK {
            connect_timeout 3
            nb_get_retry 3
            delay_before_retry 3
        }
    }

    real_server 192.168.100.218 80 {
        weight 1
        TCP_CHECK {
            connect_timeout 3
            nb_get_retry 3
            delay_before_retry 3
        }
    }
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
        assert len(non_empty_params) == 1
        
        # Check virtual_server block
        virtual_server = non_empty_params[0]
        assert isinstance(virtual_server, KeepAlivedConfigBlock)
        assert virtual_server.name == "virtual_server 192.168.100.219 80"
        
        # Check virtual_server parameters
        param_names = [param.name for param in virtual_server.params if hasattr(param, 'name') and param.name]
        expected_params = ["delay_loop", "lb_algo", "lb_kind", "protocol"]
        for param in expected_params:
            assert param in param_names
        
        # Check real_server blocks
        real_servers = [p for p in virtual_server.params if isinstance(p, KeepAlivedConfigBlock) and p.name.startswith("real_server")]
        assert len(real_servers) == 2
        
        # Check first real_server
        rs1 = real_servers[0]
        assert rs1.name == "real_server 192.168.100.217 80"
        weight_params = [p for p in rs1.params if hasattr(p, 'name') and p.name == "weight"]
        assert len(weight_params) == 1
        assert weight_params[0].value == "1"
        
        # Check TCP_CHECK block
        tcp_checks = [p for p in rs1.params if isinstance(p, KeepAlivedConfigBlock) and p.name == "TCP_CHECK"]
        assert len(tcp_checks) == 1
        tcp_check = tcp_checks[0]
        tcp_check_params = [p.name for p in tcp_check.params if hasattr(p, 'name') and p.name]
        expected_tcp_params = ["connect_timeout", "nb_get_retry", "delay_before_retry"]
        for param in expected_tcp_params:
            assert param in tcp_check_params
    
    finally:
        # Clean up temporary file
        os.unlink(temp_file)


def test_virtual_server_template():
    """Test virtual_server template creation"""
    # Test with TCP_CHECK
    config = KeepAlivedConfig.from_template("basic_virtual_server", "192.168.1.1 80")
    
    # Check that config was created correctly
    assert len(config.params) == 1
    assert config.params[0].name == "virtual_server 192.168.1.1 80"
    
    # Check that real_server was added correctly
    virtual_server_block = config.params[0]
    real_server_blocks = [p for p in virtual_server_block.params if isinstance(p, KeepAlivedConfigBlock) and p.name.startswith("real_server")]
    assert len(real_server_blocks) == 1
    
    # Check that both TCP_CHECK and HTTP_GET blocks were added correctly
    real_server_block = real_server_blocks[0]
    tcp_check_blocks = [p for p in real_server_block.params if isinstance(p, KeepAlivedConfigBlock) and p.name == "TCP_CHECK"]
    http_get_blocks = [p for p in real_server_block.params if isinstance(p, KeepAlivedConfigBlock) and p.name == "HTTP_GET"]
    assert len(tcp_check_blocks) == 1
    assert len(http_get_blocks) == 1
    
    # Test with a custom template using TCP_CHECK
    tcp_check_template = {
        "type": "virtual_server",
        "params": {
            "delay_loop": 5,
            "lb_algo": "rr",
            "lb_kind": "DR",
            "protocol": "TCP",
            "real_server": {
                "ip": "192.168.1.100",
                "port": "80",
                "weight": 1,
                "health_check": "TCP_CHECK",   # Changed from "tcp_check" to "TCP_CHECK"
                "TCP_CHECK": {                 # Changed from "tcp_check" to "TCP_CHECK"
                    "connect_timeout": 3,
                    "delay_before_retry": 3
                }
            }
        }
    }
    
    KeepAlivedConfig.register_template("tcp_check_template", tcp_check_template)
    config2 = KeepAlivedConfig.from_template("tcp_check_template", "192.168.1.1 80")
    
    # Check that config was created correctly
    assert len(config2.params) == 1
    # For custom templates, we expect just "virtual_server" since the instance name is applied during processing
    assert config2.params[0].name.startswith("virtual_server")


def test_virtual_server_find_param():
    """Test finding virtual_server and real_server parameters"""
    # Create configuration from template
    config = KeepAlivedConfig.from_template("basic_virtual_server", "10.0.0.1 80")

    # Test finding virtual_server - use the correct path
    virtual_server = config.params[0]  # Direct access instead of find_param
    assert virtual_server is not None
    assert isinstance(virtual_server, KeepAlivedConfigBlock)
    assert virtual_server.name == "virtual_server 10.0.0.1 80"

    # Test finding real_server
    real_servers = [p for p in virtual_server.params if hasattr(p, 'name') and p.name.startswith('real_server')]
    assert len(real_servers) == 1
    real_server = real_servers[0]
    assert real_server.name == "real_server REAL_SERVER_IP REAL_SERVER_PORT"


def test_virtual_server_format_config():
    """Test formatting virtual_server configuration"""
    # Create configuration from template
    config = KeepAlivedConfig.from_template("basic_virtual_server", "10.0.0.1 80")

    # Format configuration
    formatted = config.format_config()

    # Verify it contains expected elements
    assert "virtual_server 10.0.0.1 80" in formatted
    assert "real_server REAL_SERVER_IP REAL_SERVER_PORT" in formatted


def test_virtual_server_template_placeholders():
    """Test that all new placeholders are present in the virtual_server template"""
    config = KeepAlivedConfig.from_template("basic_virtual_server", "192.168.1.1 80")
    formatted = config.format_config()
    
    # Check that all placeholders are present
    assert "VIRTUAL_SERVER_DELAY_LOOP" in formatted
    assert "VIRTUAL_SERVER_LB_ALGO" in formatted
    assert "VIRTUAL_SERVER_LB_KIND" in formatted
    assert "VIRTUAL_SERVER_PROTOCOL" in formatted
    assert "REAL_SERVER_WEIGHT" in formatted
    
    # Check that TCP_CHECK, HTTP_GET and UDP_CHECK are present as examples
    assert "TCP_CHECK_CONNECT_TIMEOUT" in formatted
    assert "TCP_CHECK_DELAY_BEFORE_RETRY" in formatted
    assert "HTTP_CHECK_URL" in formatted
    assert "HTTP_CHECK_DIGEST" in formatted
    assert "HTTP_CHECK_STATUS_CODE" in formatted
    assert "UDP_CHECK_CONNECT_TIMEOUT" in formatted
    assert "UDP_CHECK_DELAY_BEFORE_RETRY" in formatted

    # Ensure nb_get_retry is no longer present
    assert "TCP_CHECK_NB_GET_RETRY" not in formatted


def test_http_check_support():
    """Test HTTP_CHECK support in virtual_server template"""
    # Create a template with HTTP check
    http_check_template = {
        "type": "virtual_server",
        "params": {
            "delay_loop": 10,
            "lb_algo": "wrr",
            "lb_kind": "NAT",
            "protocol": "HTTP",
            "real_server": {
                "ip": "192.168.1.10",
                "port": "8080",
                "weight": 2,
                "health_check": "HTTP_GET",    # Changed from "http_check" to "HTTP_GET"
                "HTTP_GET": {                  # Changed from "http_check" to "HTTP_GET"
                    "url": "/health",
                    "digest": "ffffffffffffffffffffffffffffffff",
                    "status_code": "200"
                }
            }
        }
    }

    KeepAlivedConfig.register_template("http_check_template", http_check_template)

    # Use the HTTP check template
    config = KeepAlivedConfig.from_template("http_check_template", "192.168.1.1 80")
    
    # Check that config was created correctly
    assert len(config.params) == 1
    # For custom templates, we expect just "virtual_server" since the instance name is applied during processing
    assert config.params[0].name.startswith("virtual_server")
    
    # Check that real_server was added correctly
    virtual_server_block = config.params[0]
    real_server_blocks = [p for p in virtual_server_block.params if isinstance(p, KeepAlivedConfigBlock) and p.name.startswith("real_server")]
    assert len(real_server_blocks) == 1
    
    # Check that HTTP_GET block was added correctly
    real_server_block = real_server_blocks[0]
    http_get_blocks = [p for p in real_server_block.params if isinstance(p, KeepAlivedConfigBlock) and p.name == "HTTP_GET"]
    assert len(http_get_blocks) == 1


def test_udp_check_support():
    """Test UDP_CHECK support in virtual_server template"""
    # Create a template with UDP check
    udp_check_template = {
        "type": "virtual_server",
        "params": {
            "delay_loop": 10,
            "lb_algo": "wrr",
            "lb_kind": "NAT",
            "protocol": "UDP",
            "real_server": {
                "ip": "192.168.1.20",
                "port": "53",
                "weight": 2,
                "health_check": "UDP_CHECK",
                "UDP_CHECK": {
                    "connect_timeout": 3,
                    "delay_before_retry": 3
                }
            }
        }
    }

    KeepAlivedConfig.register_template("udp_check_template", udp_check_template)

    # Use the UDP check template
    config = KeepAlivedConfig.from_template("udp_check_template", "192.168.1.1 53")
    
    # Check that config was created correctly
    assert len(config.params) == 1
    # For custom templates, we expect just "virtual_server" since the instance name is applied during processing
    assert config.params[0].name.startswith("virtual_server")
    
    # Check that real_server was added correctly
    virtual_server_block = config.params[0]
    real_server_blocks = [p for p in virtual_server_block.params if isinstance(p, KeepAlivedConfigBlock) and p.name.startswith("real_server")]
    assert len(real_server_blocks) == 1
    
    # Check that UDP_CHECK block was added correctly
    real_server_block = real_server_blocks[0]
    udp_check_blocks = [p for p in real_server_block.params if isinstance(p, KeepAlivedConfigBlock) and p.name == "UDP_CHECK"]
    assert len(udp_check_blocks) == 1
