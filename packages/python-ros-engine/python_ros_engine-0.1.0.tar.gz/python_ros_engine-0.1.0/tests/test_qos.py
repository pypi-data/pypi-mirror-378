"""
Tests for the QoS profiles in the Python ROS engine.
"""

import pytest

from pyros2.qos import DurabilityPolicy, QoSProfile, ReliabilityPolicy


class TestQoS:
    """Test cases for QoS profiles."""

    def test_qos_profile_creation(self):
        """Test QoS profile creation with default values."""
        qos = QoSProfile()
        assert qos.reliability == ReliabilityPolicy.RELIABLE
        assert qos.durability == DurabilityPolicy.VOLATILE
        assert qos.depth == 10

    def test_qos_profile_custom_values(self):
        """Test QoS profile creation with custom values."""
        qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
            depth=5,
        )
        assert qos.reliability == ReliabilityPolicy.BEST_EFFORT
        assert qos.durability == DurabilityPolicy.TRANSIENT_LOCAL
        assert qos.depth == 5

    def test_qos_profile_predefined_profiles(self):
        """Test predefined QoS profiles."""
        from pyros2.qos import QOS_PROFILE_DEFAULT

        # Test default profiles
        assert QOS_PROFILE_DEFAULT.reliability == ReliabilityPolicy.RELIABLE

    def test_qos_profile_validation(self):
        """Test QoS profile validation."""
        # Test valid profile
        QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.VOLATILE,
            depth=10,
        )
        # Should not raise any exceptions

        # Test invalid reliability type
        with pytest.raises(TypeError):
            QoSProfile(
                reliability="invalid", durability=DurabilityPolicy.VOLATILE, depth=10
            )

        # Test invalid durability type
        with pytest.raises(TypeError):
            QoSProfile(
                reliability=ReliabilityPolicy.RELIABLE, durability="invalid", depth=10
            )

        # Test invalid depth type
        with pytest.raises(TypeError):
            QoSProfile(
                reliability=ReliabilityPolicy.RELIABLE,
                durability=DurabilityPolicy.VOLATILE,
                depth="invalid",
            )

        # Test negative depth
        with pytest.raises(TypeError):
            QoSProfile(
                reliability=ReliabilityPolicy.RELIABLE,
                durability=DurabilityPolicy.VOLATILE,
                depth=-1,
            )
