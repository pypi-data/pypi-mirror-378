"""
Tests for the additional message types in the Python ROS engine.
"""

from pyros2.message import (
    Bool,
    ByteMultiArray,
    Duration,
    Empty,
    Float32,
    Float32MultiArray,
    Float64,
    Int8,
    Int16,
    Int32,
    Int32MultiArray,
    Int64,
    MultiArrayDimension,
    MultiArrayLayout,
    Time,
    UInt8,
    UInt16,
    UInt32,
    UInt64,
)


class TestAdditionalMessages:
    """Test cases for additional message types."""

    def test_int8_message(self):
        """Test Int8 message type."""
        msg = Int8(data=42)
        assert msg.data == 42

        # Test serialization/deserialization
        serialized = msg.serialize()
        deserialized = Int8.deserialize(serialized)
        assert deserialized.data == 42

    def test_int16_message(self):
        """Test Int16 message type."""
        msg = Int16(data=1000)
        assert msg.data == 1000

        # Test serialization/deserialization
        serialized = msg.serialize()
        deserialized = Int16.deserialize(serialized)
        assert deserialized.data == 1000

    def test_int32_message(self):
        """Test Int32 message type."""
        msg = Int32(data=100000)
        assert msg.data == 100000

        # Test serialization/deserialization
        serialized = msg.serialize()
        deserialized = Int32.deserialize(serialized)
        assert deserialized.data == 100000

    def test_int64_message(self):
        """Test Int64 message type."""
        msg = Int64(data=100000000000)
        assert msg.data == 100000000000

        # Test serialization/deserialization
        serialized = msg.serialize()
        deserialized = Int64.deserialize(serialized)
        assert deserialized.data == 100000000000

    def test_uint8_message(self):
        """Test UInt8 message type."""
        msg = UInt8(data=255)
        assert msg.data == 255

        # Test serialization/deserialization
        serialized = msg.serialize()
        deserialized = UInt8.deserialize(serialized)
        assert deserialized.data == 255

    def test_uint16_message(self):
        """Test UInt16 message type."""
        msg = UInt16(data=65535)
        assert msg.data == 65535

        # Test serialization/deserialization
        serialized = msg.serialize()
        deserialized = UInt16.deserialize(serialized)
        assert deserialized.data == 65535

    def test_uint32_message(self):
        """Test UInt32 message type."""
        msg = UInt32(data=4294967295)
        assert msg.data == 4294967295

        # Test serialization/deserialization
        serialized = msg.serialize()
        deserialized = UInt32.deserialize(serialized)
        assert deserialized.data == 4294967295

    def test_uint64_message(self):
        """Test UInt64 message type."""
        msg = UInt64(data=18446744073709551615)
        assert msg.data == 18446744073709551615

        # Test serialization/deserialization
        serialized = msg.serialize()
        deserialized = UInt64.deserialize(serialized)
        assert deserialized.data == 18446744073709551615

    def test_float32_message(self):
        """Test Float32 message type."""
        msg = Float32(data=3.14159)
        assert msg.data == 3.14159

        # Test serialization/deserialization
        serialized = msg.serialize()
        deserialized = Float32.deserialize(serialized)
        assert deserialized.data == 3.14159

    def test_float64_message(self):
        """Test Float64 message type."""
        msg = Float64(data=3.141592653589793)
        assert msg.data == 3.141592653589793

        # Test serialization/deserialization
        serialized = msg.serialize()
        deserialized = Float64.deserialize(serialized)
        assert deserialized.data == 3.141592653589793

    def test_bool_message(self):
        """Test Bool message type."""
        msg = Bool(data=True)
        assert msg.data

        # Test serialization/deserialization
        serialized = msg.serialize()
        deserialized = Bool.deserialize(serialized)
        assert deserialized.data

    def test_empty_message(self):
        """Test Empty message type."""
        msg = Empty()
        # Empty message should have no data attributes

        # Test serialization/deserialization
        msg.serialize()
        # Should successfully deserialize with no attributes

    def test_time_message(self):
        """Test Time message type."""
        msg = Time(secs=1234567890, nsecs=987654321)
        assert msg.secs == 1234567890
        assert msg.nsecs == 987654321

        # Test serialization/deserialization
        serialized = msg.serialize()
        deserialized = Time.deserialize(serialized)
        assert deserialized.secs == 1234567890
        assert deserialized.nsecs == 987654321

    def test_duration_message(self):
        """Test Duration message type."""
        msg = Duration(secs=100, nsecs=500000000)
        assert msg.secs == 100
        assert msg.nsecs == 500000000

        # Test serialization/deserialization
        serialized = msg.serialize()
        deserialized = Duration.deserialize(serialized)
        assert deserialized.secs == 100
        assert deserialized.nsecs == 500000000

    def test_multi_array_dimension(self):
        """Test MultiArrayDimension message type."""
        dim = MultiArrayDimension(label="test", size=10, stride=20)
        assert dim.label == "test"
        assert dim.size == 10
        assert dim.stride == 20

    def test_multi_array_layout(self):
        """Test MultiArrayLayout message type."""
        dim1 = MultiArrayDimension(label="x", size=5, stride=10)
        dim2 = MultiArrayDimension(label="y", size=3, stride=15)

        layout = MultiArrayLayout(dim=[dim1, dim2], data_offset=5)
        assert len(layout.dim) == 2
        assert layout.data_offset == 5
        assert layout.dim[0].label == "x"
        assert layout.dim[1].label == "y"

        # Test with default initialization
        layout_default = MultiArrayLayout()
        assert layout_default.dim == []
        assert layout_default.data_offset == 0

    def test_byte_multi_array(self):
        """Test ByteMultiArray message type."""
        dim = MultiArrayDimension(label="data", size=5, stride=5)
        layout = MultiArrayLayout(dim=[dim], data_offset=0)

        msg = ByteMultiArray(layout=layout, data=[1, 2, 3, 4, 5])
        assert len(msg.data) == 5
        assert msg.layout.data_offset == 0

        # Test serialization/deserialization
        serialized = msg.serialize()
        deserialized = ByteMultiArray.deserialize(serialized)
        assert len(deserialized.data) == 5
        assert deserialized.layout.data_offset == 0

    def test_int32_multi_array(self):
        """Test Int32MultiArray message type."""
        dim = MultiArrayDimension(label="data", size=3, stride=3)
        layout = MultiArrayLayout(dim=[dim], data_offset=0)

        msg = Int32MultiArray(layout=layout, data=[100, 200, 300])
        assert len(msg.data) == 3
        assert msg.data[0] == 100
        assert msg.data[1] == 200
        assert msg.data[2] == 300

        # Test serialization/deserialization
        serialized = msg.serialize()
        deserialized = Int32MultiArray.deserialize(serialized)
        assert len(deserialized.data) == 3
        assert deserialized.data[0] == 100
        assert deserialized.data[1] == 200
        assert deserialized.data[2] == 300

    def test_float32_multi_array(self):
        """Test Float32MultiArray message type."""
        dim = MultiArrayDimension(label="data", size=4, stride=4)
        layout = MultiArrayLayout(dim=[dim], data_offset=0)

        msg = Float32MultiArray(layout=layout, data=[1.1, 2.2, 3.3, 4.4])
        assert len(msg.data) == 4
        assert msg.data[0] == 1.1
        assert msg.data[1] == 2.2
        assert msg.data[2] == 3.3
        assert msg.data[3] == 4.4

        # Test serialization/deserialization
        serialized = msg.serialize()
        deserialized = Float32MultiArray.deserialize(serialized)
        assert len(deserialized.data) == 4
        assert deserialized.data[0] == 1.1
        assert deserialized.data[1] == 2.2
        assert deserialized.data[2] == 3.3
        assert deserialized.data[3] == 4.4
