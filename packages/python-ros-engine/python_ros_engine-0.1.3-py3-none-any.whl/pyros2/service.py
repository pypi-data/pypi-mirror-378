"""
Service implementation for the Python ROS engine.
"""

from typing import TYPE_CHECKING, Callable, Dict

if TYPE_CHECKING:
    from .node import Node

from .exceptions import InvalidServiceNameError
from .qos import QoSProfile


class Service:
    """
    Service server for handling requests.
    """

    # Class variable to store all services
    _service_registry: Dict[str, "Service"] = {}

    def __init__(
        self,
        node: "Node",
        srv_type: type,
        service_name: str,
        callback: Callable,
        qos_profile: QoSProfile,
    ):
        """
        Initialize a service server.

        Args:
            node: The node that owns this service
            srv_type: Type of service
            service_name: Name of the service
            callback: Callback function to execute when a request is received
            qos_profile: Quality of Service profile
        """
        if not service_name.startswith("/"):
            raise InvalidServiceNameError("Service name must start with '/'")

        self.node = node
        self.srv_type = srv_type
        self.service_name = service_name
        self._callback = callback
        self.qos_profile = qos_profile

        # Register service in registry
        Service._service_registry[service_name] = self

    def handle_request(self, request):
        """
        Handle a service request.

        Args:
            request: Service request

        Returns:
            Service response
        """
        if not isinstance(request, self.srv_type.Request):
            raise TypeError(f"Request must be of type {self.srv_type.Request.__name__}")

        return self._callback(request)

    @classmethod
    def get_service(cls, service_name: str):
        """
        Get a service by name.

        Args:
            service_name: Name of the service

        Returns:
            Service: The requested service
        """
        return cls._service_registry.get(service_name)

    @classmethod
    def clear_registry(cls):
        """
        Clear the service registry. Used for testing.
        """
        cls._service_registry.clear()
