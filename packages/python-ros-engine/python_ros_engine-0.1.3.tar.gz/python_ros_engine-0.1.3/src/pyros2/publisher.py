"""
Publisher implementation for the Python ROS engine.
"""

from typing import TYPE_CHECKING, Dict, List

if TYPE_CHECKING:
    from .node import Node
    from .subscriber import Subscriber

from .exceptions import InvalidTopicNameError
from .message import Message
from .qos import QoSProfile


class Publisher:
    """
    Publisher for sending messages to a topic.
    """

    # Class variable to store all topics and their messages
    _topic_registry: Dict[str, List[Message]] = {}
    _subscriber_registry: Dict[str, List["Subscriber"]] = {}

    def __init__(
        self, node: "Node", msg_type: type, topic_name: str, qos_profile: QoSProfile
    ):
        """
        Initialize a publisher.

        Args:
            node: The node that owns this publisher
            msg_type: Type of message to publish
            topic_name: Name of the topic
            qos_profile: Quality of Service profile
        """
        if not topic_name.startswith("/"):
            raise InvalidTopicNameError("Topic name must start with '/'")

        self.node = node
        self.msg_type = msg_type
        self.topic_name = topic_name
        self.qos_profile = qos_profile

        # Initialize topic in registry if it doesn't exist
        if topic_name not in Publisher._topic_registry:
            Publisher._topic_registry[topic_name] = []

        # Initialize subscriber registry for this topic if it doesn't exist
        if topic_name not in Publisher._subscriber_registry:
            Publisher._subscriber_registry[topic_name] = []

    def publish(self, message: Message):
        """
        Publish a message to the topic.

        Args:
            message: Message to publish
        """
        if not isinstance(message, self.msg_type):
            raise TypeError(f"Message must be of type {self.msg_type.__name__}")

        # Add message to topic registry
        Publisher._topic_registry[self.topic_name].append(message)

        # Maintain QoS depth
        if len(Publisher._topic_registry[self.topic_name]) > self.qos_profile.depth:
            Publisher._topic_registry[self.topic_name].pop(0)

        # Notify subscribers
        for subscriber in Publisher._subscriber_registry[self.topic_name]:
            subscriber._callback(message)

    @classmethod
    def register_subscriber(cls, topic_name: str, subscriber: "Subscriber"):
        """
        Register a subscriber for a topic.

        Args:
            topic_name: Name of the topic
            subscriber: Subscriber to register
        """
        if topic_name not in cls._subscriber_registry:
            cls._subscriber_registry[topic_name] = []
        cls._subscriber_registry[topic_name].append(subscriber)

    @classmethod
    def get_messages(cls, topic_name: str) -> List[Message]:
        """
        Get messages for a topic.

        Args:
            topic_name: Name of the topic

        Returns:
            List[Message]: List of messages for the topic
        """
        return cls._topic_registry.get(topic_name, [])

    @classmethod
    def clear_registry(cls):
        """
        Clear the topic and subscriber registries. Used for testing.
        """
        cls._topic_registry.clear()
        cls._subscriber_registry.clear()
