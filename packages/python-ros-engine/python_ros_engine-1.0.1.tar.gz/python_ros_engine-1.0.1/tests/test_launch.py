"""Tests for the LaunchSystem in the Python ROS engine."""

from pyros2 import LaunchDescription, LaunchSystem
from pyros2.message import String


class MockNode:
    """Mock node for testing."""

    def __init__(self, name):
        """Initialize the mock node."""
        from pyros2 import Node

        self._node = Node(name)
        self.node_name = name
        self.publisher = self._node.create_publisher(String, f"/{name}_topic")
        self.subscriber = self._node.create_subscription(
            String, f"/{name}_topic", self.callback
        )
        # Copy attributes from the internal node for easier access
        self.namespace = self._node.namespace
        self._publishers = self._node._publishers
        self._subscribers = self._node._subscribers
        self._services = self._node._services
        self._clients = self._node._clients
        self._parameters = self._node._parameters

    def callback(self, msg):
        """Mock callback."""
        pass

    def destroy_node(self):
        """Mock destroy node."""
        self._node.destroy_node()

    def get_publishers_info_by_topic(self, topic_name):
        """Get publisher info by topic."""
        return self._node.get_publishers_info_by_topic(topic_name)

    def get_subscriptions_info_by_topic(self, topic_name):
        """Get subscription info by topic."""
        return self._node.get_subscriptions_info_by_topic(topic_name)


class TestLaunchSystem:
    """Test cases for LaunchSystem."""

    def setup_method(self):
        """Clear registries before each test."""
        from pyros2.publisher import Publisher
        from pyros2.service import Service

        Publisher.clear_registry()
        Service.clear_registry()

    def test_add_node(self):
        """Test adding a node to the launch system."""
        launch_system = LaunchSystem()
        launch_system.add_node("mock_node", MockNode, "mock_node")

        assert "mock_node" in launch_system.nodes
        assert isinstance(launch_system.nodes["mock_node"], MockNode)

    def test_remove_node(self):
        """Test removing a node from the launch system."""
        launch_system = LaunchSystem()
        launch_system.add_node("mock_node", MockNode, "mock_node")

        assert "mock_node" in launch_system.nodes

        launch_system.remove_node("mock_node")
        assert "mock_node" not in launch_system.nodes

    def test_get_system_status(self):
        """Test getting system status."""
        launch_system = LaunchSystem()
        launch_system.add_node("mock_node1", MockNode, "mock_node1")
        launch_system.add_node("mock_node2", MockNode, "mock_node2")

        status = launch_system.get_system_status()

        assert "nodes" in status
        assert "topics" in status
        assert "services" in status
        assert "system_info" in status

        assert len(status["nodes"]) == 2
        assert len(status["topics"]) == 2
        assert len(status["services"]) == 0

        # Check node info
        assert "mock_node1" in status["nodes"]
        assert "mock_node2" in status["nodes"]

        # Check topic info
        assert "/mock_node1_topic" in status["topics"]
        assert "/mock_node2_topic" in status["topics"]

    def test_launch_description(self):
        """Test LaunchDescription functionality."""
        launch_description = LaunchDescription()
        launch_description.add_node(MockNode, "mock_node1")
        launch_description.add_node(MockNode, "mock_node2")

        launch_system = launch_description.execute()

        assert len(launch_system.nodes) == 2
        assert "mock_node1" in launch_system.nodes
        assert "mock_node2" in launch_system.nodes
