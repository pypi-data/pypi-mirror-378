"""
Tests for the Node class in the Python ROS engine.
"""

from pyros2 import Node
from pyros2.message import String


class TestNode:
    """Test cases for the Node class."""

    def test_node_initialization(self):
        """Test node initialization with name and namespace."""
        node = Node("test_node")
        assert node.node_name == "test_node"
        assert node.namespace == "/"

        node = Node("test_node", "/my_namespace")
        assert node.node_name == "test_node"
        assert node.namespace == "/my_namespace"

    def test_create_publisher(self):
        """Test creating a publisher."""
        node = Node("test_node")
        publisher = node.create_publisher(String, "/test_topic")

        assert "/test_topic" in node._publishers
        assert node._publishers["/test_topic"] == publisher
        assert publisher.msg_type == String
        assert publisher.topic_name == "/test_topic"

    def test_create_subscription(self):
        """Test creating a subscription."""
        node = Node("test_node")

        def callback(msg):
            pass

        subscriber = node.create_subscription(String, "/test_topic", callback)

        assert "/test_topic" in node._subscribers
        assert node._subscribers["/test_topic"] == subscriber
        assert subscriber.msg_type == String
        assert subscriber.topic_name == "/test_topic"
        assert subscriber._callback == callback

    def test_create_service(self):
        """Test creating a service."""
        node = Node("test_node")

        def callback(request):
            pass

        # Create a mock service type
        class MockService:
            Request = object
            Response = object

        service = node.create_service(MockService, "/test_service", callback)

        assert "/test_service" in node._services
        assert node._services["/test_service"] == service
        assert service.srv_type == MockService
        assert service.service_name == "/test_service"
        assert service._callback == callback

    def test_create_client(self):
        """Test creating a client."""
        node = Node("test_node")

        # Create a mock service type
        class MockService:
            Request = object
            Response = object

        client = node.create_client(MockService, "/test_service")

        assert "/test_service" in node._clients
        assert node._clients["/test_service"] == client
        assert client.srv_type == MockService
        assert client.service_name == "/test_service"

    def test_declare_parameter(self):
        """Test declaring parameters."""
        node = Node("test_node")
        param = node.declare_parameter("test_param", "default_value")

        assert "test_param" in node._parameters
        assert node._parameters["test_param"] == param
        assert param.name == "test_param"
        assert param.value == "default_value"
        assert param.type == "str"

    def test_get_parameter(self):
        """Test getting parameters."""
        node = Node("test_node")
        node.declare_parameter("test_param", "default_value")

        param = node.get_parameter("test_param")
        assert param.name == "test_param"
        assert param.value == "default_value"
        assert param.type == "str"

    def test_set_parameter(self):
        """Test setting parameters."""
        node = Node("test_node")
        node.declare_parameter("test_param", "default_value")

        result = node.set_parameter("test_param", "new_value")
        assert result
        assert node.get_parameter("test_param").value == "new_value"

    def test_get_topic_names_and_types(self):
        """Test getting topic names and types."""
        node = Node("test_node")
        node.create_publisher(String, "/test_topic")
        topics = node.get_topic_names_and_types()

        assert len(topics) == 1
        assert topics[0][0] == "/test_topic"
        assert topics[0][1] == ["String"]

    def test_get_service_names_and_types(self):
        """Test getting service names and types."""
        node = Node("test_node")

        # Create a mock service type
        class MockService:
            Request = object
            Response = object

        node.create_service(MockService, "/test_service", lambda x: x)
        services = node.get_service_names_and_types()

        assert len(services) == 1
        assert services[0][0] == "/test_service"
        assert services[0][1] == ["MockService"]
