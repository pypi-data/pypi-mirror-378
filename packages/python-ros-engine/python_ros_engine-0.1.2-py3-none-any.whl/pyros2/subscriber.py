"""
Subscriber implementation for the Python ROS engine.
"""

from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from .node import Node

from .exceptions import InvalidTopicNameError
from .message import Message
from .qos import QoSProfile


class Subscriber:
    """
    Subscriber for receiving messages from a topic.
    """

    def __init__(
        self,
        node: "Node",
        msg_type: type,
        topic_name: str,
        callback: Callable,
        qos_profile: QoSProfile,
    ):
        """
        Initialize a subscriber.

        Args:
            node: The node that owns this subscriber
            msg_type: Type of message to subscribe to
            topic_name: Name of the topic
            callback: Callback function to execute when a message is received
            qos_profile: Quality of Service profile
        """
        if not topic_name.startswith("/"):
            raise InvalidTopicNameError("Topic name must start with '/'")

        self.node = node
        self.msg_type = msg_type
        self.topic_name = topic_name
        self._callback = callback
        self.qos_profile = qos_profile

        # Register this subscriber with the publisher registry
        from .publisher import Publisher

        Publisher.register_subscriber(topic_name, self)

    def callback(self, message: Message):
        """
        Execute the callback function with the received message.

        Args:
            message: Received message
        """
        if isinstance(message, self.msg_type):
            self._callback(message)
