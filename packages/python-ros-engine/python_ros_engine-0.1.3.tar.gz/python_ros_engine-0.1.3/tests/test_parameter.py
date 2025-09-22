"""
Tests for the Parameter functionality in the Python ROS engine.
"""

import pytest

from pyros2 import Node
from pyros2.exceptions import ParameterAlreadyDeclaredError, ParameterNotDeclaredError


class TestParameter:
    """Test cases for Parameter functionality."""

    def test_parameter_declaration(self):
        """Test parameter declaration."""
        node = Node("test_node")
        param = node.declare_parameter("test_param", "default_value")

        assert param.name == "test_param"
        assert param.value == "default_value"
        assert param.type == "str"

    def test_parameter_declaration_with_type(self):
        """Test parameter declaration with explicit type."""
        node = Node("test_node")
        param = node.declare_parameter("test_param", 42, "int")

        assert param.name == "test_param"
        assert param.value == 42
        assert param.type == "int"

    def test_parameter_get(self):
        """Test parameter retrieval."""
        node = Node("test_node")
        node.declare_parameter("test_param", "default_value")

        param = node.get_parameter("test_param")
        assert param.name == "test_param"
        assert param.value == "default_value"
        assert param.type == "str"

    def test_parameter_get_nonexistent(self):
        """Test getting a non-existent parameter."""
        node = Node("test_node")

        with pytest.raises(ParameterNotDeclaredError):
            node.get_parameter("nonexistent_param")

    def test_parameter_set(self):
        """Test parameter setting."""
        node = Node("test_node")
        node.declare_parameter("test_param", "default_value")

        result = node.set_parameter("test_param", "new_value")
        assert result
        assert node.get_parameter("test_param").value == "new_value"

    def test_parameter_set_type_checking(self):
        """Test parameter setting with type checking."""
        node = Node("test_node")
        node.declare_parameter("int_param", 42, "int")

        # Setting with correct type should work
        result = node.set_parameter("int_param", 100)
        assert result
        assert node.get_parameter("int_param").value == 100

        # Setting with incorrect type should raise TypeError
        with pytest.raises(TypeError):
            node.set_parameter("int_param", "string_value")

    def test_parameter_set_nonexistent(self):
        """Test setting a non-existent parameter."""
        node = Node("test_node")

        with pytest.raises(ParameterNotDeclaredError):
            node.set_parameter("nonexistent_param", "value")

    def test_parameter_declaration_duplicate(self):
        """Test declaring a duplicate parameter."""
        node = Node("test_node")
        node.declare_parameter("test_param", "default_value")

        with pytest.raises(ParameterAlreadyDeclaredError):
            node.declare_parameter("test_param", "another_value")

    def test_parameter_callback(self):
        """Test parameter callback functionality."""
        node = Node("test_node")
        node.declare_parameter("test_param", "default_value")

        callback_calls = []

        def param_callback(params):
            callback_calls.append(params)

        node.add_on_set_parameters_callback(param_callback)

        # Set parameter to trigger callback
        node.set_parameter("test_param", "new_value")

        # Check that callback was called
        assert len(callback_calls) == 1
        assert len(callback_calls[0]) == 1
        assert callback_calls[0][0].name == "test_param"
        assert callback_calls[0][0].value == "new_value"
