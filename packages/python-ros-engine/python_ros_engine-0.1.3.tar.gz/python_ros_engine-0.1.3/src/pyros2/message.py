"""
Base message classes for the Python ROS engine.
"""

import json
from dataclasses import dataclass
from typing import List


class Message:
    """
    Base class for all ROS messages.
    """

    def __init__(self):
        pass

    def serialize(self) -> bytes:
        """
        Serialize the message to bytes.
        """

        def serialize_object(obj):
            # Handle dataclass objects (including nested ones)
            if hasattr(obj, "__dataclass_fields__"):
                result = {}
                for field_name in obj.__dataclass_fields__:
                    field_value = getattr(obj, field_name)
                    result[field_name] = serialize_object(field_value)
                return result
            # Handle lists
            elif isinstance(obj, list):
                return [serialize_object(item) for item in obj]
            # Handle basic types
            else:
                return obj

        # Create a dictionary representation of the message
        result = {}
        for field_name in self.__dataclass_fields__:
            field_value = getattr(self, field_name)
            result[field_name] = serialize_object(field_value)

        return json.dumps(result).encode("utf-8")

    @classmethod
    def deserialize(cls, data: bytes):
        """
        Deserialize bytes to a message instance.
        """
        data_dict = json.loads(data.decode("utf-8"))
        return cls(**data_dict)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.__dict__})"


@dataclass
class String(Message):
    """
    String message type.
    """

    data: str = ""


@dataclass
class Int8(Message):
    """
    8-bit integer message type.
    """

    data: int = 0


@dataclass
class Int16(Message):
    """
    16-bit integer message type.
    """

    data: int = 0


@dataclass
class Int32(Message):
    """
    32-bit integer message type.
    """

    data: int = 0


@dataclass
class Int64(Message):
    """
    64-bit integer message type.
    """

    data: int = 0


@dataclass
class UInt8(Message):
    """
    8-bit unsigned integer message type.
    """

    data: int = 0


@dataclass
class UInt16(Message):
    """
    16-bit unsigned integer message type.
    """

    data: int = 0


@dataclass
class UInt32(Message):
    """
    32-bit unsigned integer message type.
    """

    data: int = 0


@dataclass
class UInt64(Message):
    """
    64-bit unsigned integer message type.
    """

    data: int = 0


@dataclass
class Float32(Message):
    """
    32-bit float message type.
    """

    data: float = 0.0


@dataclass
class Float64(Message):
    """
    64-bit float message type.
    """

    data: float = 0.0


@dataclass
class Bool(Message):
    """
    Boolean message type.
    """

    data: bool = False


@dataclass
class Empty(Message):
    """
    Empty message type.
    """

    pass


@dataclass
class MultiArrayDimension:
    """
    Dimension description for multi-dimensional arrays.
    """

    label: str = ""
    size: int = 0
    stride: int = 0


@dataclass
class MultiArrayLayout:
    """
    Layout description for multi-dimensional arrays.
    """

    dim: List[MultiArrayDimension] = None
    data_offset: int = 0

    def __post_init__(self):
        if self.dim is None:
            self.dim = []
        # Reconstruct MultiArrayDimension objects from dictionaries if needed
        elif (
            isinstance(self.dim, list)
            and len(self.dim) > 0
            and isinstance(self.dim[0], dict)
        ):
            reconstructed_dims = []
            for dim_dict in self.dim:
                if isinstance(dim_dict, dict):
                    dim = MultiArrayDimension(
                        label=dim_dict.get("label", ""),
                        size=dim_dict.get("size", 0),
                        stride=dim_dict.get("stride", 0),
                    )
                    reconstructed_dims.append(dim)
                else:
                    reconstructed_dims.append(dim_dict)
            self.dim = reconstructed_dims


@dataclass
class ByteMultiArray(Message):
    """
    Multi-array of bytes.
    """

    layout: MultiArrayLayout = None
    data: List[int] = None

    def __post_init__(self):
        if self.layout is None:
            self.layout = MultiArrayLayout()
        elif isinstance(self.layout, dict):
            # Reconstruct layout from dictionary
            dim_list = []
            for dim_dict in self.layout.get("dim", []):
                if isinstance(dim_dict, dict):
                    dim = MultiArrayDimension(
                        label=dim_dict.get("label", ""),
                        size=dim_dict.get("size", 0),
                        stride=dim_dict.get("stride", 0),
                    )
                    dim_list.append(dim)
                else:
                    dim_list.append(dim_dict)
            self.layout = MultiArrayLayout(
                dim=dim_list, data_offset=self.layout.get("data_offset", 0)
            )
        if self.data is None:
            self.data = []


@dataclass
class Int8MultiArray(Message):
    """
    Multi-array of Int8 values.
    """

    layout: MultiArrayLayout = None
    data: List[int] = None

    def __post_init__(self):
        if self.layout is None:
            self.layout = MultiArrayLayout()
        elif isinstance(self.layout, dict):
            # Reconstruct layout from dictionary
            dim_list = []
            for dim_dict in self.layout.get("dim", []):
                if isinstance(dim_dict, dict):
                    dim = MultiArrayDimension(
                        label=dim_dict.get("label", ""),
                        size=dim_dict.get("size", 0),
                        stride=dim_dict.get("stride", 0),
                    )
                    dim_list.append(dim)
                else:
                    dim_list.append(dim_dict)
            self.layout = MultiArrayLayout(
                dim=dim_list, data_offset=self.layout.get("data_offset", 0)
            )
        if self.data is None:
            self.data = []


@dataclass
class Int16MultiArray(Message):
    """
    Multi-array of Int16 values.
    """

    layout: MultiArrayLayout = None
    data: List[int] = None

    def __post_init__(self):
        if self.layout is None:
            self.layout = MultiArrayLayout()
        elif isinstance(self.layout, dict):
            # Reconstruct layout from dictionary
            dim_list = []
            for dim_dict in self.layout.get("dim", []):
                if isinstance(dim_dict, dict):
                    dim = MultiArrayDimension(
                        label=dim_dict.get("label", ""),
                        size=dim_dict.get("size", 0),
                        stride=dim_dict.get("stride", 0),
                    )
                    dim_list.append(dim)
                else:
                    dim_list.append(dim_dict)
            self.layout = MultiArrayLayout(
                dim=dim_list, data_offset=self.layout.get("data_offset", 0)
            )
        if self.data is None:
            self.data = []


@dataclass
class Int32MultiArray(Message):
    """
    Multi-array of Int32 values.
    """

    layout: MultiArrayLayout = None
    data: List[int] = None

    def __post_init__(self):
        if self.layout is None:
            self.layout = MultiArrayLayout()
        elif isinstance(self.layout, dict):
            # Reconstruct layout from dictionary
            dim_list = []
            for dim_dict in self.layout.get("dim", []):
                if isinstance(dim_dict, dict):
                    dim = MultiArrayDimension(
                        label=dim_dict.get("label", ""),
                        size=dim_dict.get("size", 0),
                        stride=dim_dict.get("stride", 0),
                    )
                    dim_list.append(dim)
                else:
                    dim_list.append(dim_dict)
            self.layout = MultiArrayLayout(
                dim=dim_list, data_offset=self.layout.get("data_offset", 0)
            )
        if self.data is None:
            self.data = []


@dataclass
class Int64MultiArray(Message):
    """
    Multi-array of Int64 values.
    """

    layout: MultiArrayLayout = None
    data: List[int] = None

    def __post_init__(self):
        if self.layout is None:
            self.layout = MultiArrayLayout()
        elif isinstance(self.layout, dict):
            # Reconstruct layout from dictionary
            dim_list = []
            for dim_dict in self.layout.get("dim", []):
                if isinstance(dim_dict, dict):
                    dim = MultiArrayDimension(
                        label=dim_dict.get("label", ""),
                        size=dim_dict.get("size", 0),
                        stride=dim_dict.get("stride", 0),
                    )
                    dim_list.append(dim)
                else:
                    dim_list.append(dim_dict)
            self.layout = MultiArrayLayout(
                dim=dim_list, data_offset=self.layout.get("data_offset", 0)
            )
        if self.data is None:
            self.data = []


@dataclass
class UInt8MultiArray(Message):
    """
    Multi-array of UInt8 values.
    """

    layout: MultiArrayLayout = None
    data: List[int] = None

    def __post_init__(self):
        if self.layout is None:
            self.layout = MultiArrayLayout()
        elif isinstance(self.layout, dict):
            # Reconstruct layout from dictionary
            dim_list = []
            for dim_dict in self.layout.get("dim", []):
                if isinstance(dim_dict, dict):
                    dim = MultiArrayDimension(
                        label=dim_dict.get("label", ""),
                        size=dim_dict.get("size", 0),
                        stride=dim_dict.get("stride", 0),
                    )
                    dim_list.append(dim)
                else:
                    dim_list.append(dim_dict)
            self.layout = MultiArrayLayout(
                dim=dim_list, data_offset=self.layout.get("data_offset", 0)
            )
        if self.data is None:
            self.data = []


@dataclass
class UInt16MultiArray(Message):
    """
    Multi-array of UInt16 values.
    """

    layout: MultiArrayLayout = None
    data: List[int] = None

    def __post_init__(self):
        if self.layout is None:
            self.layout = MultiArrayLayout()
        elif isinstance(self.layout, dict):
            # Reconstruct layout from dictionary
            dim_list = []
            for dim_dict in self.layout.get("dim", []):
                if isinstance(dim_dict, dict):
                    dim = MultiArrayDimension(
                        label=dim_dict.get("label", ""),
                        size=dim_dict.get("size", 0),
                        stride=dim_dict.get("stride", 0),
                    )
                    dim_list.append(dim)
                else:
                    dim_list.append(dim_dict)
            self.layout = MultiArrayLayout(
                dim=dim_list, data_offset=self.layout.get("data_offset", 0)
            )
        if self.data is None:
            self.data = []


@dataclass
class UInt32MultiArray(Message):
    """
    Multi-array of UInt32 values.
    """

    layout: MultiArrayLayout = None
    data: List[int] = None

    def __post_init__(self):
        if self.layout is None:
            self.layout = MultiArrayLayout()
        elif isinstance(self.layout, dict):
            # Reconstruct layout from dictionary
            dim_list = []
            for dim_dict in self.layout.get("dim", []):
                if isinstance(dim_dict, dict):
                    dim = MultiArrayDimension(
                        label=dim_dict.get("label", ""),
                        size=dim_dict.get("size", 0),
                        stride=dim_dict.get("stride", 0),
                    )
                    dim_list.append(dim)
                else:
                    dim_list.append(dim_dict)
            self.layout = MultiArrayLayout(
                dim=dim_list, data_offset=self.layout.get("data_offset", 0)
            )
        if self.data is None:
            self.data = []


@dataclass
class UInt64MultiArray(Message):
    """
    Multi-array of UInt64 values.
    """

    layout: MultiArrayLayout = None
    data: List[int] = None

    def __post_init__(self):
        if self.layout is None:
            self.layout = MultiArrayLayout()
        elif isinstance(self.layout, dict):
            # Reconstruct layout from dictionary
            dim_list = []
            for dim_dict in self.layout.get("dim", []):
                if isinstance(dim_dict, dict):
                    dim = MultiArrayDimension(
                        label=dim_dict.get("label", ""),
                        size=dim_dict.get("size", 0),
                        stride=dim_dict.get("stride", 0),
                    )
                    dim_list.append(dim)
                else:
                    dim_list.append(dim_dict)
            self.layout = MultiArrayLayout(
                dim=dim_list, data_offset=self.layout.get("data_offset", 0)
            )
        if self.data is None:
            self.data = []


@dataclass
class Float32MultiArray(Message):
    """
    Multi-array of Float32 values.
    """

    layout: MultiArrayLayout = None
    data: List[float] = None

    def __post_init__(self):
        if self.layout is None:
            self.layout = MultiArrayLayout()
        elif isinstance(self.layout, dict):
            # Reconstruct layout from dictionary
            dim_list = []
            for dim_dict in self.layout.get("dim", []):
                if isinstance(dim_dict, dict):
                    dim = MultiArrayDimension(
                        label=dim_dict.get("label", ""),
                        size=dim_dict.get("size", 0),
                        stride=dim_dict.get("stride", 0),
                    )
                    dim_list.append(dim)
                else:
                    dim_list.append(dim_dict)
            self.layout = MultiArrayLayout(
                dim=dim_list, data_offset=self.layout.get("data_offset", 0)
            )
        if self.data is None:
            self.data = []


@dataclass
class Float64MultiArray(Message):
    """
    Multi-array of Float64 values.
    """

    layout: MultiArrayLayout = None
    data: List[float] = None

    def __post_init__(self):
        if self.layout is None:
            self.layout = MultiArrayLayout()
        elif isinstance(self.layout, dict):
            # Reconstruct layout from dictionary
            dim_list = []
            for dim_dict in self.layout.get("dim", []):
                if isinstance(dim_dict, dict):
                    dim = MultiArrayDimension(
                        label=dim_dict.get("label", ""),
                        size=dim_dict.get("size", 0),
                        stride=dim_dict.get("stride", 0),
                    )
                    dim_list.append(dim)
                else:
                    dim_list.append(dim_dict)
            self.layout = MultiArrayLayout(
                dim=dim_list, data_offset=self.layout.get("data_offset", 0)
            )
        if self.data is None:
            self.data = []


@dataclass
class Time(Message):
    """
    Time message type.
    """

    secs: int = 0
    nsecs: int = 0


@dataclass
class Duration(Message):
    """
    Duration message type.
    """

    secs: int = 0
    nsecs: int = 0
