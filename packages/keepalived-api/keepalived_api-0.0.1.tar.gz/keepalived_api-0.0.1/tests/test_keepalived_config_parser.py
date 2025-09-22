import os
import sys
import pytest
from unittest import mock

SRC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src")
sys.path.append(SRC_DIR)

from keepalived_config.keepalived_config_parser import (
    KeepAlivedConfigParser,
    KeepAlivedConfig,
    KeepAlivedConfigBlock,
    KeepAlivedConfigParam,
)


def test_invalid_parse_string():
    invalid_items = [
        None,
        123,
        0.3,
        True,
        {"a": "b"},
        ["a", "b"],
    ]

    def test_invalid_parse_string(config_string):
        with pytest.raises(TypeError):
            KeepAlivedConfigParser().parse_string(config_string)

    for config_string in invalid_items:
        test_invalid_parse_string(config_string)


def test_parse_string():
    valid_config_strings = [
        " ",
        "\n",
        "\n\n\n",
        "param",
        "param value",
        "param value # comment",
        "param value # inline comment",
        "param # inline comment",
        "param # inline comment\n",
        "param # inline comment\n\n",
        "# comment\nparam value",
        "# comment\nparam value\n",
        "# comment\nparam value\n\n",
        "# comment\n\nparam value",
        "param1 value1\nparam2 value2",
        "block {\n}",
        "block {\nparam value\n}",
        "block {\nparam value\n}\n",
        "block {\nparam value\n}\n\n",
        "block1 {\nparam1 value1\nblock2 {\nparam2 value2\n}\n}",
        "block1 {\nparam1 value1\n}\nblock2 {\nparam2 value2\n}",
    ]

    def test_valid_parse_string(config_string):
        cfg = KeepAlivedConfigParser().parse_string(config_string)
        assert cfg
        assert isinstance(cfg, KeepAlivedConfig)

    for config_string in valid_config_strings:
        test_valid_parse_string(config_string)


def test_parse_file():
    def verify_valid_parse_file(with_empty_lines):
        with mock.patch("os.path.exists", return_value=True) as exists_mock, mock.patch(
            "builtins.open", mock.mock_open(read_data="")
        ):
            with (
                mock.patch(
                    "keepalived_config.keepalived_config_parser.KeepAlivedConfigParser.parse_string",
                    return_value=KeepAlivedConfig(config_file="my_file"),
                ) as mock_parse_string,
            ):
                exists_mock.reset_mock()
                cfg = KeepAlivedConfigParser().parse_file(
                    "my_file", keep_empty_lines=with_empty_lines
                )
                exists_mock.assert_called_once_with("my_file")
                assert cfg
                assert isinstance(cfg, KeepAlivedConfig)
                assert cfg.config_file == "my_file"
                mock_parse_string.assert_called_once_with("", with_empty_lines)

    for with_empty_lines in [True, False]:
        verify_valid_parse_file(with_empty_lines)


def test_parse_complex_config():
    """Test parsing a complex keepalived configuration"""
    complex_config = """# Global Configuration
global_defs {
    notification_email {
        admin@example.com
        support@example.com
    }
    notification_email_from keepalived@example.com
    smtp_server 127.0.0.1
    smtp_connect_timeout 30
    router_id LVS_MAIN
}

# VRRP Configuration
vrrp_instance VI_1 {
    state MASTER
    interface eth0
    virtual_router_id 51
    priority 100
    advert_int 1
    authentication {
        auth_type PASS
        auth_pass secret_password
    }
    virtual_ipaddress {
        192.168.1.10/24
        192.168.1.11/24
    }
    notify_master /etc/keepalived/master.sh
}

# Virtual Server Configuration
virtual_server 192.168.1.10 80 {
    delay_loop 6
    lb_algo rr
    lb_kind NAT
    persistence_timeout 50
    protocol TCP

    real_server 10.0.0.1 80 {
        weight 1
        TCP_CHECK {
            connect_timeout 3
            retry 3
            delay_before_retry 3
        }
    }

    real_server 10.0.0.2 80 {
        weight 1
        TCP_CHECK {
            connect_timeout 3
            retry 3
            delay_before_retry 3
        }
    }
}
"""
    
    parser = KeepAlivedConfigParser()
    config = parser.parse_string(complex_config)
    
    # Verify overall structure
    assert isinstance(config, KeepAlivedConfig)