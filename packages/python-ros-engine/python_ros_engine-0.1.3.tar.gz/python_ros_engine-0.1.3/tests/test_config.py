"""
Tests for the Hydra configuration system in the Python ROS engine.
"""

import os

from config.hydra_config import (
    BridgeConfig,
    NodeConfig,
    ParameterConfig,
    PublisherConfig,
    ROSConfig,
    ServiceConfig,
    SubscriberConfig,
    load_config,
    save_config,
)
from pyros2.qos import DurabilityPolicy, QoSProfile, ReliabilityPolicy


class TestHydraConfig:
    """Test cases for Hydra configuration system."""

    def test_node_config(self):
        """Test NodeConfig dataclass."""
        config = NodeConfig(name="test_node", namespace="/test")
        assert config.name == "test_node"
        assert config.namespace == "/test"

    def test_publisher_config(self):
        """Test PublisherConfig dataclass."""
        qos = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
            depth=5,
        )
        config = PublisherConfig(topic="/test_topic", qos=qos)
        assert config.topic == "/test_topic"
        assert config.qos.reliability == ReliabilityPolicy.RELIABLE
        assert config.qos.durability == DurabilityPolicy.TRANSIENT_LOCAL
        assert config.qos.depth == 5

    def test_subscriber_config(self):
        """Test SubscriberConfig dataclass."""
        qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.VOLATILE,
            depth=10,
        )
        config = SubscriberConfig(topic="/test_topic", qos=qos)
        assert config.topic == "/test_topic"
        assert config.qos.reliability == ReliabilityPolicy.BEST_EFFORT
        assert config.qos.durability == DurabilityPolicy.VOLATILE
        assert config.qos.depth == 10

    def test_service_config(self):
        """Test ServiceConfig dataclass."""
        qos = QoSProfile(depth=20)
        config = ServiceConfig(name="/test_service", qos=qos)
        assert config.name == "/test_service"
        assert config.qos.depth == 20

    def test_parameter_config(self):
        """Test ParameterConfig dataclass."""
        config = ParameterConfig(name="param1", value="test", type="string")
        assert config.name == "param1"
        assert config.value == "test"
        assert config.type == "string"

    def test_bridge_config(self):
        """Test BridgeConfig dataclass."""
        config = BridgeConfig(host="192.168.1.1", port=11312, protocol="xmlrpc")
        assert config.host == "192.168.1.1"
        assert config.port == 11312
        assert config.protocol == "xmlrpc"

    def test_ros_config(self):
        """Test ROSConfig dataclass."""
        node_config = NodeConfig(name="test_node", namespace="/test")
        publisher_config = PublisherConfig(topic="/test_topic")
        subscriber_config = SubscriberConfig(topic="/test_topic")
        service_config = ServiceConfig(name="/test_service")
        parameter_config = ParameterConfig(name="param1", value="test", type="string")
        bridge_config = BridgeConfig(host="192.168.1.1", port=11312)

        config = ROSConfig(
            node=node_config,
            publisher=publisher_config,
            subscriber=subscriber_config,
            service=service_config,
            parameters={"param1": parameter_config},
            bridge=bridge_config,
        )

        assert config.node.name == "test_node"
        assert config.publisher.topic == "/test_topic"
        assert config.subscriber.topic == "/test_topic"
        assert config.service.name == "/test_service"
        assert config.parameters["param1"].value == "test"
        assert config.bridge.host == "192.168.1.1"

    def test_load_config(self):
        """Test loading configuration from file."""
        # Test with the default config file
        config_path = os.path.join(
            os.path.dirname(__file__), "..", "config", "config.yaml"
        )
        if os.path.exists(config_path):
            config = load_config(config_path)
            assert config.node.name == "default_node"
            assert config.node.namespace == "/"

    def test_save_config(self):
        """Test saving configuration to file."""
        # Create a test config
        node_config = NodeConfig(name="test_node", namespace="/test")
        config = ROSConfig(node=node_config)

        # Save to temporary file
        test_config_path = os.path.join(os.path.dirname(__file__), "test_config.yaml")
        save_config(config, test_config_path)

        # Check that file was created
        assert os.path.exists(test_config_path)

        # Load and verify
        loaded_config = load_config(test_config_path)
        assert loaded_config.node.name == "test_node"
        assert loaded_config.node.namespace == "/test"

        # Clean up
        os.remove(test_config_path)
