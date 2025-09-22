"""
Node implementation for the Python ROS engine.
"""

import time
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable, Dict, List

if TYPE_CHECKING:
    from .publisher import Publisher
    from .subscriber import Subscriber
    from .service import Service
    from .client import Client

from .exceptions import (
    NodeNotInitializedError,
    ParameterAlreadyDeclaredError,
    ParameterNotDeclaredError,
)
from .qos import QoSProfile


@dataclass
class Parameter:
    """
    A parameter with a name, value, and type.
    """

    name: str
    value: Any
    type: str


class Node:
    """
    Base class for a ROS node.
    """

    def __init__(self, node_name: str, namespace: str = "/"):
        """
        Initialize a ROS node.

        Args:
            node_name: Name of the node
            namespace: Namespace for the node
        """
        self.node_name = node_name
        self.namespace = namespace
        self._parameters: Dict[str, Parameter] = {}
        self._publishers: Dict[str, "Publisher"] = {}
        self._subscribers: Dict[str, "Subscriber"] = {}
        self._services: Dict[str, "Service"] = {}
        self._clients: Dict[str, "Client"] = {}
        self._parameter_callbacks: List[Callable] = []
        self._is_initialized = True
        self._is_shutdown = False

    def create_publisher(
        self, msg_type: type, topic_name: str, qos_profile: QoSProfile = None
    ):
        """
        Create a publisher for a topic.

        Args:
            msg_type: Type of message to publish
            topic_name: Name of the topic
            qos_profile: Quality of Service profile

        Returns:
            Publisher: The created publisher
        """
        if not self._is_initialized:
            raise NodeNotInitializedError(
                "Node must be initialized before creating publishers"
            )

        from .publisher import Publisher

        if qos_profile is None:
            qos_profile = QoSProfile()

        publisher = Publisher(self, msg_type, topic_name, qos_profile)
        self._publishers[topic_name] = publisher
        return publisher

    def create_subscription(
        self,
        msg_type: type,
        topic_name: str,
        callback: Callable,
        qos_profile: QoSProfile = None,
    ):
        """
        Create a subscription to a topic.

        Args:
            msg_type: Type of message to subscribe to
            topic_name: Name of the topic
            callback: Callback function to execute when a message is received
            qos_profile: Quality of Service profile

        Returns:
            Subscriber: The created subscriber
        """
        if not self._is_initialized:
            raise NodeNotInitializedError(
                "Node must be initialized before creating subscriptions"
            )

        from .subscriber import Subscriber

        if qos_profile is None:
            qos_profile = QoSProfile()

        subscriber = Subscriber(self, msg_type, topic_name, callback, qos_profile)
        self._subscribers[topic_name] = subscriber
        return subscriber

    def create_service(
        self,
        srv_type: type,
        service_name: str,
        callback: Callable,
        qos_profile: QoSProfile = None,
    ):
        """
        Create a service server.

        Args:
            srv_type: Type of service
            service_name: Name of the service
            callback: Callback function to execute when a request is received
            qos_profile: Quality of Service profile

        Returns:
            Service: The created service
        """
        if not self._is_initialized:
            raise NodeNotInitializedError(
                "Node must be initialized before creating services"
            )

        from .service import Service

        if qos_profile is None:
            qos_profile = QoSProfile()

        service = Service(self, srv_type, service_name, callback, qos_profile)
        self._services[service_name] = service
        return service

    def create_client(
        self, srv_type: type, service_name: str, qos_profile: QoSProfile = None
    ):
        """
        Create a service client.

        Args:
            srv_type: Type of service
            service_name: Name of the service
            qos_profile: Quality of Service profile

        Returns:
            Client: The created client
        """
        if not self._is_initialized:
            raise NodeNotInitializedError(
                "Node must be initialized before creating clients"
            )

        from .client import Client

        if qos_profile is None:
            qos_profile = QoSProfile()

        client = Client(self, srv_type, service_name, qos_profile)
        self._clients[service_name] = client
        return client

    def create_timer(self, timer_period_sec: float, callback: Callable):
        """
        Create a timer that calls the callback function periodically.

        Args:
            timer_period_sec: Timer period in seconds
            callback: Callback function to execute when timer expires

        Returns:
            Timer: The created timer
        """
        if not self._is_initialized:
            raise NodeNotInitializedError(
                "Node must be initialized before creating timers"
            )

        from .timer import Timer

        timer = Timer(timer_period_sec, callback)
        return timer

    def declare_parameter(
        self, name: str, default_value: Any = None, parameter_type: str = None
    ):
        """
        Declare a parameter with a name and default value.

        Args:
            name: Name of the parameter
            default_value: Default value for the parameter
            parameter_type: Type of the parameter (inferred if not provided)
        """
        if name in self._parameters:
            raise ParameterAlreadyDeclaredError(
                f"Parameter '{name}' is already declared"
            )

        if parameter_type is None:
            parameter_type = type(default_value).__name__

        parameter = Parameter(name, default_value, parameter_type)
        self._parameters[name] = parameter
        return parameter

    def get_parameter(self, name: str) -> Parameter:
        """
        Get a parameter by name.

        Args:
            name: Name of the parameter

        Returns:
            Parameter: The requested parameter
        """
        if name not in self._parameters:
            raise ParameterNotDeclaredError(f"Parameter '{name}' is not declared")

        return self._parameters[name]

    def set_parameter(self, name: str, value: Any) -> bool:
        """
        Set a parameter value.

        Args:
            name: Name of the parameter
            value: New value for the parameter

        Returns:
            bool: True if parameter was set successfully
        """
        if name not in self._parameters:
            raise ParameterNotDeclaredError(f"Parameter '{name}' is not declared")

        # Type checking
        expected_type = self._parameters[name].type
        actual_type = type(value).__name__

        if expected_type != actual_type:
            raise TypeError(
                f"Parameter '{name}' expects type '{expected_type}' "
                f"but got '{actual_type}'"
            )

        self._parameters[name].value = value

        # Call parameter callbacks
        for callback in self._parameter_callbacks:
            callback([self._parameters[name]])

        return True

    def add_on_set_parameters_callback(self, callback: Callable):
        """
        Add a callback to be called when parameters are set.

        Args:
            callback: Callback function to execute when parameters change
        """
        self._parameter_callbacks.append(callback)

    def get_topic_names_and_types(self) -> List[tuple]:
        """
        Get list of topics and their types.

        Returns:
            List[tuple]: List of (topic_name, topic_types) tuples
        """
        topics = []
        for topic_name, publisher in self._publishers.items():
            topics.append((topic_name, [publisher.msg_type.__name__]))
        for topic_name, subscriber in self._subscribers.items():
            if not any(topic[0] == topic_name for topic in topics):
                topics.append((topic_name, [subscriber.msg_type.__name__]))
        return topics

    def get_service_names_and_types(self) -> List[tuple]:
        """
        Get list of services and their types.

        Returns:
            List[tuple]: List of (service_name, service_types) tuples
        """
        services = []
        for service_name, service in self._services.items():
            services.append((service_name, [service.srv_type.__name__]))
        for service_name, client in self._clients.items():
            if not any(service[0] == service_name for service in services):
                services.append((service_name, [client.srv_type.__name__]))
        return services

    def get_publishers_info_by_topic(self, topic_name: str) -> List[Dict[str, Any]]:
        """
        Get information about publishers for a topic.

        Args:
            topic_name: Name of the topic

        Returns:
            List[Dict]: List of publisher information dictionaries
        """
        if topic_name in self._publishers:
            publisher = self._publishers[topic_name]
            return [
                {
                    "node_name": self.node_name,
                    "topic_name": topic_name,
                    "topic_type": publisher.msg_type.__name__,
                }
            ]
        return []

    def get_subscriptions_info_by_topic(self, topic_name: str) -> List[Dict[str, Any]]:
        """
        Get information about subscriptions for a topic.

        Args:
            topic_name: Name of the topic

        Returns:
            List[Dict]: List of subscription information dictionaries
        """
        if topic_name in self._subscribers:
            subscriber = self._subscribers[topic_name]
            return [
                {
                    "node_name": self.node_name,
                    "topic_name": topic_name,
                    "topic_type": subscriber.msg_type.__name__,
                }
            ]
        return []

    def spin(self):
        """
        Spin the node to process callbacks.
        """
        if not self._is_initialized:
            raise NodeNotInitializedError("Node must be initialized before spinning")

        print(f"Spinning node '{self.node_name}'...")

        # In a real implementation, this would process callbacks asynchronously
        # For now, we'll just run a simple loop
        try:
            while not self._is_shutdown:
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("Shutting down node...")
            self.destroy_node()

    def spin_once(self, timeout_sec: float = 0.1):
        """
        Process one callback and return.

        Args:
            timeout_sec: Timeout in seconds
        """
        if not self._is_initialized:
            raise NodeNotInitializedError("Node must be initialized before spinning")

        # In a real implementation, this would process one callback
        time.sleep(min(timeout_sec, 0.1))

    def destroy_node(self):
        """
        Destroy the node and clean up resources.
        """
        self._is_shutdown = True
        print(f"Node '{self.node_name}' destroyed.")
