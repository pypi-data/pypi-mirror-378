"""
Tests for the Discovery functionality in the Python ROS engine.
"""

from pyros2 import Node
from pyros2.discovery import Discovery
from pyros2.message import String
from pyros2.publisher import Publisher
from pyros2.qos import QoSProfile
from pyros2.service import Service


class TestDiscovery:
    """Test cases for Discovery functionality."""

    def setup_method(self):
        """Clear registries before each test."""
        Publisher.clear_registry()
        Service.clear_registry()

    def test_get_all_topics(self):
        """Test getting all topics."""
        # Initially no topics
        topics = Discovery.get_all_topics()
        assert len(topics) == 0

        # Create a node and publisher
        node = Node("test_node")
        Publisher(node, String, "/test_topic", QoSProfile())

        # Now we should have one topic
        topics = Discovery.get_all_topics()
        assert len(topics) == 1
        assert "/test_topic" in topics

    def test_get_all_services(self):
        """Test getting all services."""
        # Initially no services
        services = Discovery.get_all_services()
        assert len(services) == 0

        # Create a node and service
        node = Node("test_node")

        def callback(request):
            pass

        # Create a mock service type
        class MockService:
            Request = object
            Response = object

        Service(node, MockService, "/test_service", callback, QoSProfile())

        # Now we should have one service
        services = Discovery.get_all_services()
        assert len(services) == 1
        assert "/test_service" in services

    def test_get_topic_types(self):
        """Test getting topic types."""
        # Create a node and publisher
        node = Node("test_node")
        Publisher(node, String, "/test_topic", QoSProfile())

        # Get topic types
        types = Discovery.get_topic_types("/test_topic")
        assert len(types) > 0
        # In our implementation, we return a dummy type
        assert "std_msgs/String" in types

        # Non-existent topic should return empty list
        types = Discovery.get_topic_types("/nonexistent_topic")
        assert len(types) == 0

    def test_get_service_types(self):
        """Test getting service types."""
        # Create a node and callback
        node = Node("test_node")

        def callback(request):
            pass

        # Create a mock service type
        class MockService:
            Request = object
            Response = object

        Service(node, MockService, "/test_service", callback, QoSProfile())

        # Get service types
        types = Discovery.get_service_types("/test_service")
        assert len(types) > 0
        # In our implementation, we return a dummy type
        assert "example_interfaces/AddTwoInts" in types

        # Non-existent service should return empty list
        types = Discovery.get_service_types("/nonexistent_service")
        assert len(types) == 0

    def test_get_nodes(self):
        """Test getting all nodes."""
        # In our current implementation, this returns an empty list
        # since we don't have a node registry
        nodes = Discovery.get_nodes()
        assert isinstance(nodes, list)
