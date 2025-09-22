"""
Client implementation for the Python ROS engine.
"""

import asyncio
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .node import Node

from .exceptions import ServiceNotFoundError
from .qos import QoSProfile


class Client:
    """
    Service client for calling services.
    """

    def __init__(
        self, node: "Node", srv_type: type, service_name: str, qos_profile: QoSProfile
    ):
        """
        Initialize a service client.

        Args:
            node: The node that owns this client
            srv_type: Type of service
            service_name: Name of the service
            qos_profile: Quality of Service profile
        """
        self.node = node
        self.srv_type = srv_type
        self.service_name = service_name
        self.qos_profile = qos_profile

    def call(self, request):
        """
        Call a service synchronously.

        Args:
            request: Service request

        Returns:
            Service response
        """
        from .service import Service

        service = Service.get_service(self.service_name)
        if service is None:
            raise ServiceNotFoundError(f"Service '{self.service_name}' not found")

        return service.handle_request(request)

    async def call_async(self, request):
        """
        Call a service asynchronously.

        Args:
            request: Service request

        Returns:
            Service response
        """
        # In a real implementation, this would be truly asynchronous
        # For now, we'll just use asyncio.sleep to simulate async behavior
        await asyncio.sleep(0.01)
        return self.call(request)
