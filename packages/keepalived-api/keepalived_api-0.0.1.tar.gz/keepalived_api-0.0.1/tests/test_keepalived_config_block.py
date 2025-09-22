import os
import sys
import pytest

SRC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src")
sys.path.append(SRC_DIR)

from keepalived_config.keepalived_config_block import (
    KeepAlivedConfigBlock,
    KeepAlivedConfigParam,
    KeepAlivedConfigConstants,
)
from keepalived_config.keepalived_config_comment import (
    KeepAlivedConfigCommentTypes,
    KeepAlivedConfigComment,
)


class InvalidValue:
    def __str__(self):
        raise Exception("Invalid __str__")


def test_valid_init():
    valid_items = [
        ("my_type", "myname", []),
        ("my_type", "", []),
        (
            "mytype",
            "myname",
            [KeepAlivedConfigComment("comment"), KeepAlivedConfigComment("comment")],
        ),
    ]

    for type_name, name, comments in valid_items:
        block = KeepAlivedConfigBlock(type_name=type_name, name=name, comments=comments)
        assert block.name == f"{type_name}{' ' + name if name else ''}"
        assert block.value == ""
        assert block.comments == comments


def test_invalid_init():
    invalid_items = [
        (InvalidValue(), "value", []),
        (True, "value", []),
        ("param", 123, {"a": "b"}),
        ("param", 0.3, ["comment"]),
        ("param", "value", ["comment", "comment"]),
    ]

    def test_invalid_init(type_name, name, comments):
        with pytest.raises(TypeError):
            KeepAlivedConfigBlock(type_name=type_name, name=name, comments=comments)

    for type_name, name, comments in invalid_items:
        test_invalid_init(type_name, name, comments)


def test_params():
    block = KeepAlivedConfigBlock("my_type")
    assert block.name == "my_type"
    assert block.params == []

    block.add_param(KeepAlivedConfigBlock("my_type_2"))
    assert len(block.params) == 1
    assert isinstance(block.params[0], KeepAlivedConfigBlock)

    block.add_param(KeepAlivedConfigParam("mykey", "myvalue"))
    assert len(block.params) == 2
    assert isinstance(block.params[1], KeepAlivedConfigParam)


def test_invalid_add_param():
    invalid_params = [None, 123, 3.2, True, "param", KeepAlivedConfigComment("comment")]

    block = KeepAlivedConfigBlock("my_type")
    assert block.params == []

    def test_invalid_add_param(param):
        with pytest.raises(TypeError):
            block.add_param(param)

    for param in invalid_params:
        test_invalid_add_param(param)


def test_to_str():
    block = KeepAlivedConfigBlock("my_type", "myname")

    assert block.to_str() == "my_type myname {\n}"
    assert (
        block.to_str(1)
        == f"{KeepAlivedConfigConstants.get_indent(1)}my_type myname {{\n"
        + f"{KeepAlivedConfigConstants.get_indent(1)}}}"
    )

    block.add_param(KeepAlivedConfigBlock("my_type_2", "myname_2"))
    block.params[0].add_param(KeepAlivedConfigParam("mysubkey", "mysubvalue"))
    block.add_param(
        KeepAlivedConfigParam(
            "mykey", "myvalue", comments=[KeepAlivedConfigComment("comment")]
        )
    )

    assert (
        block.to_str()
        == "my_type myname {\n"
        + f"{KeepAlivedConfigConstants.get_indent(1)}my_type_2 myname_2 {{\n"
        + f"{KeepAlivedConfigConstants.get_indent(2)}mysubkey mysubvalue\n"
        + f"{KeepAlivedConfigConstants.get_indent(1)}}}\n"
        + f"{KeepAlivedConfigConstants.get_indent(1)}{KeepAlivedConfigComment.COMMENT_INDICATOR} comment\n"
        + f"{KeepAlivedConfigConstants.get_indent(1)}mykey myvalue\n"
        + "}"
    )


def test_add_vrrp_instance_success():
    """Test successfully adding a VRRP instance."""
    block = KeepAlivedConfigBlock("global_defs")
    
    # Add a valid VRRP instance
    result = block.add_vrrp_instance(
        instance_name="VI_1",
        state="MASTER",
        interface="eth0",
        virtual_router_id=51,
        priority=100,
        advert_int=1
    )
    
    # Verify the operation succeeded and returns the created block
    assert isinstance(result, KeepAlivedConfigBlock)
    assert result.name == "vrrp_instance VI_1"
    assert len(block.params) == 1
    assert block.params[0] is result
    
    # Verify the parameters were added correctly
    vrrp_block = block.params[0]
    param_names = [param.name for param in vrrp_block.params]
    expected_params = ["state", "interface", "virtual_router_id", "priority", "advert_int"]
    for param in expected_params:
        assert param in param_names

def test_add_vrrp_instance_duplicate():
    """Test that adding a VRRP instance returns the created block even if name duplicates exist."""
    block = KeepAlivedConfigBlock("global_defs")
    
    # Add the first instance (should succeed)
    result1 = block.add_vrrp_instance(instance_name="VI_1", state="MASTER", interface="eth0", 
                                     virtual_router_id=51, priority=100, advert_int=1)
    assert isinstance(result1, KeepAlivedConfigBlock)
    assert len(block.params) == 1
    
    # Add another instance with the same name (should still create and return a block)
    result2 = block.add_vrrp_instance(instance_name="VI_1", state="BACKUP", interface="eth1", 
                                     virtual_router_id=52, priority=90, advert_int=2)
    assert isinstance(result2, KeepAlivedConfigBlock)
    assert len(block.params) == 2
    assert result2 != result1  # Different instances


def test_remove_vrrp_instance_success():
    """Test successfully removing an existing VRRP instance."""
    block = KeepAlivedConfigBlock("global_defs")
    
    # Add two VRRP instances
    block.add_vrrp_instance(instance_name="VI_1", state="MASTER", interface="eth0", 
                            virtual_router_id=51, priority=100, advert_int=1)
    block.add_vrrp_instance(instance_name="VI_2", state="BACKUP", interface="eth1", 
                            virtual_router_id=52, priority=90, advert_int=1)
    
    assert len(block.params) == 2
    
    # Remove the first instance
    result = block.remove_vrrp_instance("VI_1")
    assert result is True
    assert len(block.params) == 1
    assert block.params[0].name == "vrrp_instance VI_2"

def test_remove_vrrp_instance_not_found():
    """Test that removing a non-existent VRRP instance returns False."""
    block = KeepAlivedConfigBlock("global_defs")
    
    # The block starts empty
    result = block.remove_vrrp_instance("VI_1")
    assert result is False
    assert len(block.params) == 0
    
    # Add one instance and try to remove a different one
    block.add_vrrp_instance(instance_name="VI_1", state="MASTER", interface="eth0", 
                            virtual_router_id=51, priority=100, advert_int=1)
    result = block.remove_vrrp_instance("VI_2")
    assert result is False
    assert len(block.params) == 1


def test_vrrp_instance_validation():
    """Test validation of VRRP instance parameters raises ValueError for invalid inputs."""
    block = KeepAlivedConfigBlock("global_defs")
    
    # Test with valid parameters
    result = block.add_vrrp_instance(
        instance_name="VI_1",
        state="MASTER",
        interface="eth0",
        virtual_router_id=51,
        priority=100,
        advert_int=1
    )
    assert isinstance(result, KeepAlivedConfigBlock)
    block.remove_vrrp_instance("VI_1")  # Clean up
    
    # Test with invalid state
    with pytest.raises(ValueError):
        block.add_vrrp_instance(
            instance_name="VI_1",
            state="INVALID_STATE",
            interface="eth0",
            virtual_router_id=51,
            priority=100,
            advert_int=1
        )
    
    # Test with invalid virtual_router_id (too low)
    with pytest.raises(ValueError):
        block.add_vrrp_instance(
            instance_name="VI_2",
            state="MASTER",
            interface="eth0",
            virtual_router_id=0,
            priority=100,
            advert_int=1
        )
    
    # Test with invalid virtual_router_id (too high)
    with pytest.raises(ValueError):
        block.add_vrrp_instance(
            instance_name="VI_2",
            state="MASTER",
            interface="eth0",
            virtual_router_id=256,
            priority=100,
            advert_int=1
        )
    
    # Test with invalid priority (too low)
    with pytest.raises(ValueError):
        block.add_vrrp_instance(
            instance_name="VI_2",
            state="MASTER",
            interface="eth0",
            virtual_router_id=51,
            priority=0,
            advert_int=1
        )
    
    # Test with invalid priority (too high)
    with pytest.raises(ValueError):
        block.add_vrrp_instance(
            instance_name="VI_2",
            state="MASTER",
            interface="eth0",
            virtual_router_id=51,
            priority=256,
            advert_int=1
        )
    
    # Test with invalid advert_int (too low)
    with pytest.raises(ValueError):
        block.add_vrrp_instance(
            instance_name="VI_2",
            state="MASTER",
            interface="eth0",
            virtual_router_id=51,
            priority=100,
            advert_int=0
        )
    
    # Test with invalid advert_int (too high)
    with pytest.raises(ValueError):
        block.add_vrrp_instance(
            instance_name="VI_2",
            state="MASTER",
            interface="eth0",
            virtual_router_id=51,
            priority=100,
            advert_int=256
        )
