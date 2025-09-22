"""
Quality of Service (QoS) profiles for the Python ROS engine.
"""

from dataclasses import dataclass
from enum import Enum


class ReliabilityPolicy(Enum):
    """
    Reliability policy for message delivery.
    """

    RELIABLE = "reliable"  # Guaranteed delivery
    BEST_EFFORT = "best_effort"  # No guarantee of delivery


class DurabilityPolicy(Enum):
    """
    Durability policy for message persistence.
    """

    TRANSIENT_LOCAL = "transient_local"  # Replays last message for late subscribers
    VOLATILE = "volatile"  # No message replay


@dataclass
class QoSProfile:
    """
    Quality of Service profile defining communication policies.
    """

    reliability: ReliabilityPolicy = ReliabilityPolicy.RELIABLE
    durability: DurabilityPolicy = DurabilityPolicy.VOLATILE
    depth: int = 10

    def __post_init__(self):
        if not isinstance(self.reliability, ReliabilityPolicy):
            raise TypeError("reliability must be a ReliabilityPolicy enum")
        if not isinstance(self.durability, DurabilityPolicy):
            raise TypeError("durability must be a DurabilityPolicy enum")
        if not isinstance(self.depth, int) or self.depth < 0:
            raise TypeError("depth must be a non-negative integer")


# Predefined QoS profiles
QOS_PROFILE_DEFAULT = QoSProfile()
QOS_PROFILE_SYSTEM_DEFAULT = QoSProfile()
QOS_PROFILE_SENSOR_DATA = QoSProfile(
    reliability=ReliabilityPolicy.BEST_EFFORT,
    durability=DurabilityPolicy.VOLATILE,
    depth=5,
)
QOS_PROFILE_PARAMETERS = QoSProfile(
    reliability=ReliabilityPolicy.RELIABLE,
    durability=DurabilityPolicy.TRANSIENT_LOCAL,
    depth=1000,
)
QOS_PROFILE_SERVICES = QoSProfile(
    reliability=ReliabilityPolicy.RELIABLE,
    durability=DurabilityPolicy.VOLATILE,
    depth=10,
)
