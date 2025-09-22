"""
Tests for the MessageTranslator class in the Python ROS engine.
"""

from pyros2.message import (
    Bool,
    Float32,
    Int32,
    Int32MultiArray,
    MultiArrayDimension,
    MultiArrayLayout,
    String,
)
from pyros2.message_translator import MessageTranslator


class TestMessageTranslator:
    """Test cases for MessageTranslator functionality."""

    def test_pyros_to_ros_string(self):
        """Test translation of String message from Python ROS to native ROS."""
        pyros_msg = String(data="test message")
        ros_msg = MessageTranslator.pyros_to_ros(pyros_msg, "std_msgs/String")

        assert ros_msg["_type"] == "std_msgs/String"
        assert ros_msg["data"] == "test message"

    def test_pyros_to_ros_int32(self):
        """Test translation of Int32 message from Python ROS to native ROS."""
        pyros_msg = Int32(data=42)
        ros_msg = MessageTranslator.pyros_to_ros(pyros_msg, "std_msgs/Int32")

        assert ros_msg["_type"] == "std_msgs/Int32"
        assert ros_msg["data"] == 42

    def test_pyros_to_ros_float32(self):
        """Test translation of Float32 message from Python ROS to native ROS."""
        pyros_msg = Float32(data=3.14)
        ros_msg = MessageTranslator.pyros_to_ros(pyros_msg, "std_msgs/Float32")

        assert ros_msg["_type"] == "std_msgs/Float32"
        assert ros_msg["data"] == 3.14

    def test_pyros_to_ros_bool(self):
        """Test translation of Bool message from Python ROS to native ROS."""
        pyros_msg = Bool(data=True)
        ros_msg = MessageTranslator.pyros_to_ros(pyros_msg, "std_msgs/Bool")

        assert ros_msg["_type"] == "std_msgs/Bool"
        assert ros_msg["data"]

    def test_ros_to_pyros_string(self):
        """Test translation of String message from native ROS to Python ROS."""
        ros_msg = {"_type": "std_msgs/String", "data": "test message"}

        pyros_msg = MessageTranslator.ros_to_pyros(ros_msg, String)
        assert isinstance(pyros_msg, String)
        assert pyros_msg.data == "test message"

    def test_ros_to_pyros_int32(self):
        """Test translation of Int32 message from native ROS to Python ROS."""
        ros_msg = {"_type": "std_msgs/Int32", "data": 42}

        pyros_msg = MessageTranslator.ros_to_pyros(ros_msg, Int32)
        assert isinstance(pyros_msg, Int32)
        assert pyros_msg.data == 42

    def test_ros_to_pyros_float32(self):
        """Test translation of Float32 message from native ROS to Python ROS."""
        ros_msg = {"_type": "std_msgs/Float32", "data": 3.14}

        pyros_msg = MessageTranslator.ros_to_pyros(ros_msg, Float32)
        assert isinstance(pyros_msg, Float32)
        assert pyros_msg.data == 3.14

    def test_ros_to_pyros_bool(self):
        """Test translation of Bool message from native ROS to Python ROS."""
        ros_msg = {"_type": "std_msgs/Bool", "data": True}

        pyros_msg = MessageTranslator.ros_to_pyros(ros_msg, Bool)
        assert isinstance(pyros_msg, Bool)
        assert pyros_msg.data

    def test_get_pyros_type(self):
        """Test getting Python ROS engine message type from native ROS type."""
        pyros_type = MessageTranslator.get_pyros_type("std_msgs/String")
        assert pyros_type == String

        pyros_type = MessageTranslator.get_pyros_type("std_msgs/Int32")
        assert pyros_type == Int32

        pyros_type = MessageTranslator.get_pyros_type("std_msgs/Float32")
        assert pyros_type == Float32

        pyros_type = MessageTranslator.get_pyros_type("std_msgs/Bool")
        assert pyros_type == Bool

        # Test non-existent type
        pyros_type = MessageTranslator.get_pyros_type("std_msgs/NonExistent")
        assert pyros_type is None

    def test_get_ros_type(self):
        """Test getting native ROS message type from Python ROS engine type."""
        ros_type = MessageTranslator.get_ros_type(String)
        assert ros_type == "std_msgs/String"

        ros_type = MessageTranslator.get_ros_type(Int32)
        assert ros_type == "std_msgs/Int32"

        ros_type = MessageTranslator.get_ros_type(Float32)
        assert ros_type == "std_msgs/Float32"

        ros_type = MessageTranslator.get_ros_type(Bool)
        assert ros_type == "std_msgs/Bool"

    def test_pyros_to_ros_multi_array(self):
        """Test translation of MultiArray message from Python ROS to native ROS."""
        dim1 = MultiArrayDimension(label="x", size=5, stride=10)
        dim2 = MultiArrayDimension(label="y", size=3, stride=15)
        layout = MultiArrayLayout(dim=[dim1, dim2], data_offset=5)
        pyros_msg = Int32MultiArray(layout=layout, data=[1, 2, 3, 4, 5])

        ros_msg = MessageTranslator.pyros_to_ros(pyros_msg, "std_msgs/Int32MultiArray")

        assert ros_msg["_type"] == "std_msgs/Int32MultiArray"
        assert ros_msg["data"] == [1, 2, 3, 4, 5]
        assert "layout" in ros_msg
        assert ros_msg["layout"]["data_offset"] == 5
        assert len(ros_msg["layout"]["dim"]) == 2
        assert ros_msg["layout"]["dim"][0]["label"] == "x"
        assert ros_msg["layout"]["dim"][1]["label"] == "y"

    def test_ros_to_pyros_multi_array(self):
        """Test translation of MultiArray message from native ROS to Python ROS."""
        ros_msg = {
            "_type": "std_msgs/Int32MultiArray",
            "layout": {
                "dim": [
                    {"label": "x", "size": 5, "stride": 10},
                    {"label": "y", "size": 3, "stride": 15},
                ],
                "data_offset": 5,
            },
            "data": [1, 2, 3, 4, 5],
        }

        pyros_msg = MessageTranslator.ros_to_pyros(ros_msg, Int32MultiArray)
        assert isinstance(pyros_msg, Int32MultiArray)
        assert pyros_msg.data == [1, 2, 3, 4, 5]
        assert pyros_msg.layout.data_offset == 5
        assert len(pyros_msg.layout.dim) == 2
        assert pyros_msg.layout.dim[0].label == "x"
        assert pyros_msg.layout.dim[1].label == "y"
