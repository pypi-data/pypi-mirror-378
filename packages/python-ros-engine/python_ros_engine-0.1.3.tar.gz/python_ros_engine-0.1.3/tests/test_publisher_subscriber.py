"""
Tests for the Publisher and Subscriber classes in the Python ROS engine.
"""

from pyros2 import Node
from pyros2.message import String
from pyros2.publisher import Publisher
from pyros2.qos import QoSProfile
from pyros2.subscriber import Subscriber


class TestPublisherSubscriber:
    """Test cases for Publisher and Subscriber classes."""

    def setup_method(self):
        """Clear registries before each test."""
        Publisher.clear_registry()

    def test_publisher_creation(self):
        """Test publisher creation."""
        node = Node("test_node")
        publisher = Publisher(node, String, "/test_topic", QoSProfile())

        assert publisher.node == node
        assert publisher.msg_type == String
        assert publisher.topic_name == "/test_topic"
        assert isinstance(publisher.qos_profile, QoSProfile)

    def test_publisher_publish(self):
        """Test publisher publish functionality."""
        node = Node("test_node")
        publisher = Publisher(node, String, "/test_topic", QoSProfile())

        msg = String()
        msg.data = "test message"

        publisher.publish(msg)

        # Check that message was added to registry
        messages = Publisher.get_messages("/test_topic")
        assert len(messages) == 1
        assert messages[0].data == "test message"

    def test_subscriber_creation(self):
        """Test subscriber creation."""
        node = Node("test_node")

        def callback(msg):
            pass

        subscriber = Subscriber(node, String, "/test_topic", callback, QoSProfile())

        assert subscriber.node == node
        assert subscriber.msg_type == String
        assert subscriber.topic_name == "/test_topic"
        assert subscriber._callback == callback
        assert isinstance(subscriber.qos_profile, QoSProfile)

    def test_publisher_subscriber_interaction(self):
        """Test publisher and subscriber interaction."""
        node = Node("test_node")

        received_messages = []

        def callback(msg):
            received_messages.append(msg.data)

        # Create subscriber first
        Subscriber(node, String, "/test_topic", callback, QoSProfile())

        # Create publisher
        publisher = Publisher(node, String, "/test_topic", QoSProfile())

        # Publish messages
        msg1 = String()
        msg1.data = "message 1"
        publisher.publish(msg1)

        msg2 = String()
        msg2.data = "message 2"
        publisher.publish(msg2)

        # Check that subscriber received messages
        assert len(received_messages) == 2
        assert received_messages[0] == "message 1"
        assert received_messages[1] == "message 2"

    def test_qos_depth_limit(self):
        """Test that QoS depth limits the number of stored messages."""
        node = Node("test_node")

        # Create publisher with depth of 2
        publisher = Publisher(node, String, "/test_topic", QoSProfile(depth=2))

        # Publish 3 messages
        for i in range(3):
            msg = String()
            msg.data = f"message {i}"
            publisher.publish(msg)

        # Check that only 2 messages are stored
        messages = Publisher.get_messages("/test_topic")
        assert len(messages) == 2
        assert messages[0].data == "message 1"
        assert messages[1].data == "message 2"
