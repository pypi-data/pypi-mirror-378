"""
Message translation layer for bridging Python ROS engine with native ROS.
"""

from typing import Any, Dict, Type

from .message import (
    Bool,
    ByteMultiArray,
    Duration,
    Empty,
    Float32,
    Float32MultiArray,
    Float64,
    Float64MultiArray,
    Int8,
    Int8MultiArray,
    Int16,
    Int16MultiArray,
    Int32,
    Int32MultiArray,
    Int64,
    Int64MultiArray,
    Message,
    MultiArrayDimension,
    MultiArrayLayout,
    String,
    Time,
    UInt8,
    UInt8MultiArray,
    UInt16,
    UInt16MultiArray,
    UInt32,
    UInt32MultiArray,
    UInt64,
    UInt64MultiArray,
)


class MessageTranslator:
    """
    Handles translation between Python ROS engine messages and native ROS messages.
    """

    # Mapping of native ROS message types to Python ROS engine message types
    _type_mapping = {
        # Primitive types
        "std_msgs/Bool": Bool,
        "std_msgs/String": String,
        "std_msgs/Int8": Int8,
        "std_msgs/Int16": Int16,
        "std_msgs/Int32": Int32,
        "std_msgs/Int64": Int64,
        "std_msgs/UInt8": UInt8,
        "std_msgs/UInt16": UInt16,
        "std_msgs/UInt32": UInt32,
        "std_msgs/UInt64": UInt64,
        "std_msgs/Float32": Float32,
        "std_msgs/Float64": Float64,
        "std_msgs/Empty": Empty,
        "std_msgs/Time": Time,
        "std_msgs/Duration": Duration,
        # Multi-array types
        "std_msgs/ByteMultiArray": ByteMultiArray,
        "std_msgs/Int8MultiArray": Int8MultiArray,
        "std_msgs/Int16MultiArray": Int16MultiArray,
        "std_msgs/Int32MultiArray": Int32MultiArray,
        "std_msgs/Int64MultiArray": Int64MultiArray,
        "std_msgs/UInt8MultiArray": UInt8MultiArray,
        "std_msgs/UInt16MultiArray": UInt16MultiArray,
        "std_msgs/UInt32MultiArray": UInt32MultiArray,
        "std_msgs/UInt64MultiArray": UInt64MultiArray,
        "std_msgs/Float32MultiArray": Float32MultiArray,
        "std_msgs/Float64MultiArray": Float64MultiArray,
    }

    @classmethod
    def pyros_to_ros(cls, message: Message, ros_message_type: str) -> Dict[str, Any]:
        """
        Translate a Python ROS engine message to a native ROS message format.

        Args:
            message: Python ROS engine message
            ros_message_type: Native ROS message type (e.g., "std_msgs/String")

        Returns:
            Dict: Native ROS message in dictionary format
        """
        # For now, we'll use a simple JSON-based translation
        # In a real implementation, this would convert to the actual ROS
        # message format
        ros_msg = {}
        ros_msg["_type"] = ros_message_type

        # Copy all attributes from the Python ROS message
        for key, value in message.__dict__.items():
            if isinstance(value, MultiArrayLayout):
                ros_msg[key] = cls._translate_layout(value)
            elif isinstance(value, list):
                ros_msg[key] = cls._translate_list(value)
            else:
                ros_msg[key] = value

        return ros_msg

    @classmethod
    def ros_to_pyros(
        cls, ros_message: Dict[str, Any], pyros_message_type: Type[Message]
    ) -> Message:
        """
        Translate a native ROS message to a Python ROS engine message.

        Args:
            ros_message: Native ROS message in dictionary format
            pyros_message_type: Python ROS engine message type

        Returns:
            Message: Python ROS engine message
        """
        # Create a new instance of the target message type
        pyros_msg = pyros_message_type()

        # Copy all attributes from the ROS message
        for key, value in ros_message.items():
            if key == "_type":
                continue  # Skip the type field
            elif isinstance(value, dict) and "dim" in value:
                # This is likely a MultiArrayLayout
                setattr(pyros_msg, key, cls._translate_ros_layout(value))
            elif (
                isinstance(value, list)
                and len(value) > 0
                and isinstance(value[0], dict)
            ):
                # This might be a list of MultiArrayDimension objects
                setattr(pyros_msg, key, cls._translate_ros_dimension_list(value))
            else:
                setattr(pyros_msg, key, value)

        return pyros_msg

    @classmethod
    def get_pyros_type(cls, ros_message_type: str) -> Type[Message]:
        """
        Get the corresponding Python ROS engine message type for a native ROS
        message type.

        Args:
            ros_message_type: Native ROS message type (e.g., "std_msgs/String")

        Returns:
            Type[Message]: Corresponding Python ROS engine message type
        """
        return cls._type_mapping.get(ros_message_type)

    @classmethod
    def get_ros_type(cls, pyros_message_type: Type[Message]) -> str:
        """
        Get the corresponding native ROS message type for a Python ROS engine
        message type.

        Args:
            pyros_message_type: Python ROS engine message type

        Returns:
            str: Corresponding native ROS message type
        """
        # Reverse lookup in the mapping
        for ros_type, pyros_type in cls._type_mapping.items():
            if pyros_type == pyros_message_type:
                return ros_type
        return None

    @staticmethod
    def _translate_layout(layout: MultiArrayLayout) -> Dict[str, Any]:
        """
        Translate a MultiArrayLayout to ROS format.

        Args:
            layout: MultiArrayLayout object

        Returns:
            Dict: ROS-compatible layout dictionary
        """
        ros_layout = {}
        ros_layout["dim"] = []
        for dimension in layout.dim:
            dim_dict = {
                "label": dimension.label,
                "size": dimension.size,
                "stride": dimension.stride,
            }
            ros_layout["dim"].append(dim_dict)
        ros_layout["data_offset"] = layout.data_offset
        return ros_layout

    @staticmethod
    def _translate_list(lst: list) -> list:
        """
        Translate a list of values.

        Args:
            lst: List of values

        Returns:
            list: Translated list
        """
        # For simple lists, just return as is
        return lst

    @staticmethod
    def _translate_ros_layout(ros_layout: Dict[str, Any]) -> MultiArrayLayout:
        """
        Translate a ROS layout dictionary to MultiArrayLayout.

        Args:
            ros_layout: ROS layout dictionary

        Returns:
            MultiArrayLayout: Python ROS engine layout object
        """
        layout = MultiArrayLayout()
        layout.data_offset = ros_layout.get("data_offset", 0)

        for dim_dict in ros_layout.get("dim", []):
            dimension = MultiArrayDimension(
                label=dim_dict.get("label", ""),
                size=dim_dict.get("size", 0),
                stride=dim_dict.get("stride", 0),
            )
            layout.dim.append(dimension)

        return layout

    @staticmethod
    def _translate_ros_dimension_list(ros_dim_list: list) -> list:
        """
        Translate a list of ROS dimension dictionaries to MultiArrayDimension objects.

        Args:
            ros_dim_list: List of ROS dimension dictionaries

        Returns:
            list: List of MultiArrayDimension objects
        """
        dimensions = []
        for dim_dict in ros_dim_list:
            dimension = MultiArrayDimension(
                label=dim_dict.get("label", ""),
                size=dim_dict.get("size", 0),
                stride=dim_dict.get("stride", 0),
            )
            dimensions.append(dimension)
        return dimensions
