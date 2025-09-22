"""
Tests for the Message classes in the Python ROS engine.
"""

from pyros2.message import Bool, Float32, Int32, Message, String


class TestMessage:
    """Test cases for Message classes."""

    def test_base_message_creation(self):
        """Test base message creation."""
        msg = Message()
        assert isinstance(msg, Message)

    def test_string_message(self):
        """Test String message functionality."""
        msg = String()
        assert msg.data == ""

        msg = String("test data")
        assert msg.data == "test data"

    def test_int32_message(self):
        """Test Int32 message functionality."""
        msg = Int32()
        assert msg.data == 0

        msg = Int32(42)
        assert msg.data == 42

    def test_float32_message(self):
        """Test Float32 message functionality."""
        msg = Float32()
        assert msg.data == 0.0

        msg = Float32(3.14)
        assert msg.data == 3.14

    def test_bool_message(self):
        """Test Bool message functionality."""
        msg = Bool()
        assert not msg.data

        msg = Bool(True)
        assert msg.data

    def test_message_serialization(self):
        """Test message serialization and deserialization."""
        # Test String message
        original_msg = String("test serialization")
        serialized_data = original_msg.serialize()
        deserialized_msg = String.deserialize(serialized_data)

        assert isinstance(serialized_data, bytes)
        assert deserialized_msg.data == "test serialization"

        # Test Int32 message
        original_msg = Int32(123)
        serialized_data = original_msg.serialize()
        deserialized_msg = Int32.deserialize(serialized_data)

        assert isinstance(serialized_data, bytes)
        assert deserialized_msg.data == 123

        # Test Float32 message
        original_msg = Float32(3.14159)
        serialized_data = original_msg.serialize()
        deserialized_msg = Float32.deserialize(serialized_data)

        assert isinstance(serialized_data, bytes)
        assert deserialized_msg.data == 3.14159

        # Test Bool message
        original_msg = Bool(True)
        serialized_data = original_msg.serialize()
        deserialized_msg = Bool.deserialize(serialized_data)

        assert isinstance(serialized_data, bytes)
        assert deserialized_msg.data
