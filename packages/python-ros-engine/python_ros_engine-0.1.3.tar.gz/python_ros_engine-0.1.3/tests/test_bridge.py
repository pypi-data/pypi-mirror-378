"""
Tests for the Bridge functionality in the Python ROS engine.
"""

import pytest

from pyros2.bridge import Bridge
from pyros2.exceptions import BridgeConnectionError


class TestBridge:
    """Test cases for Bridge functionality."""

    def test_bridge_initialization(self):
        """Test bridge initialization with default values."""
        bridge = Bridge()
        assert bridge.host == "localhost"
        assert bridge.port == 11311

    def test_bridge_initialization_custom_values(self):
        """Test bridge initialization with custom values."""
        bridge = Bridge("192.168.1.100", 11312)
        assert bridge.host == "192.168.1.100"
        assert bridge.port == 11312

    def test_bridge_connection_failure(self):
        """Test bridge connection failure handling."""
        # Create bridge with invalid host/port
        bridge = Bridge("invalid_host", 99999)

        # Connection should fail
        with pytest.raises(BridgeConnectionError):
            bridge.connect()

    def test_discover_ros_nodes_failure(self):
        """Test ROS node discovery failure handling."""
        bridge = Bridge("invalid_host", 99999)

        # Discovery should fail
        with pytest.raises(BridgeConnectionError):
            bridge.discover_ros_nodes()

    def test_discover_ros_topics_failure(self):
        """Test ROS topic discovery failure handling."""
        bridge = Bridge("invalid_host", 99999)

        # Discovery should fail
        with pytest.raises(BridgeConnectionError):
            bridge.discover_ros_topics()

    def test_discover_ros_services_failure(self):
        """Test ROS service discovery failure handling."""
        bridge = Bridge("invalid_host", 99999)

        # Discovery should fail
        with pytest.raises(BridgeConnectionError):
            bridge.discover_ros_services()
