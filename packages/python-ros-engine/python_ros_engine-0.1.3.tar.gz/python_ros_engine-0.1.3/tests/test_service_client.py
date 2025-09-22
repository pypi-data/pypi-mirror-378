"""
Tests for the Service and Client classes in the Python ROS engine.
"""

from pyros2 import Node
from pyros2.client import Client
from pyros2.qos import QoSProfile
from pyros2.service import Service


class TestServiceClient:
    """Test cases for Service and Client classes."""

    def setup_method(self):
        """Clear registries before each test."""
        Service.clear_registry()

    def test_service_creation(self):
        """Test service creation."""
        node = Node("test_node")

        def callback(request):
            pass

        # Create a mock service type
        class MockService:
            Request = object
            Response = object

        service = Service(node, MockService, "/test_service", callback, QoSProfile())

        assert service.node == node
        assert service.srv_type == MockService
        assert service.service_name == "/test_service"
        assert service._callback == callback
        assert isinstance(service.qos_profile, QoSProfile)

    def test_client_creation(self):
        """Test client creation."""
        node = Node("test_node")

        # Create a mock service type
        class MockService:
            Request = object
            Response = object

        client = Client(node, MockService, "/test_service", QoSProfile())

        assert client.node == node
        assert client.srv_type == MockService
        assert client.service_name == "/test_service"
        assert isinstance(client.qos_profile, QoSProfile)

    def test_service_client_interaction(self):
        """Test service and client interaction."""
        node = Node("test_node")

        # Create a mock service type
        class MockService:
            class Request:
                def __init__(self, a=0, b=0):
                    self.a = a
                    self.b = b

            class Response:
                def __init__(self, sum=0):
                    self.sum = sum

        # Service callback that adds two numbers
        def add_two_ints_callback(request):
            response = MockService.Response()
            response.sum = request.a + request.b
            return response

        # Create service
        Service(node, MockService, "/add_two_ints", add_two_ints_callback, QoSProfile())

        # Create client
        client = Client(node, MockService, "/add_two_ints", QoSProfile())

        # Make a request
        request = MockService.Request(3, 4)
        response = client.call(request)

        # Check response
        assert response.sum == 7

    def test_async_service_client_interaction(self):
        """Test async service and client interaction."""
        node = Node("test_node")

        # Create a mock service type
        class MockService:
            class Request:
                def __init__(self, a=0, b=0):
                    self.a = a
                    self.b = b

            class Response:
                def __init__(self, sum=0):
                    self.sum = sum

        # Service callback that adds two numbers
        def add_two_ints_callback(request):
            response = MockService.Response()
            response.sum = request.a + request.b
            return response

        # Create service
        Service(node, MockService, "/add_two_ints", add_two_ints_callback, QoSProfile())

        # Create client
        client = Client(node, MockService, "/add_two_ints", QoSProfile())

        # Make an async request
        import asyncio

        async def test_async_call():
            request = MockService.Request(5, 6)
            response = await client.call_async(request)
            return response

        response = asyncio.run(test_async_call())

        # Check response
        assert response.sum == 11
