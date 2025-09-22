"""
Bridge implementation for interacting with native ROS nodes.
"""

import xmlrpc.client
from typing import Any, Dict, List

from .exceptions import BridgeConnectionError


class Bridge:
    """
    Bridge for discovering and interacting with native ROS nodes.
    """

    def __init__(self, host: str = "localhost", port: int = 11311):
        """
        Initialize the ROS bridge.

        Args:
            host: ROS master host
            port: ROS master port
        """
        self.host = host
        self.port = port
        self._master_uri = f"http://{host}:{port}"
        self._master = None

    def connect(self):
        """
        Connect to the ROS master.
        """
        try:
            self._master = xmlrpc.client.ServerProxy(self._master_uri)
            # Test connection
            code, msg, val = self._master.getUri("/")
            if code != 1:
                raise BridgeConnectionError(f"Failed to connect to ROS master: {msg}")
        except Exception as e:
            raise BridgeConnectionError(
                "Failed to connect to ROS master at " f"{self._master_uri}: {str(e)}"
            )

    def discover_ros_nodes(self) -> List[str]:
        """
        Discover all native ROS nodes.

        Returns:
            List[str]: List of ROS node names
        """
        if self._master is None:
            self.connect()

        try:
            code, msg, nodes = self._master.getSystemState("/")
            if code == 1:
                # Extract unique node names from the system state
                node_names = set()
                for publisher in nodes[0]:  # publishers
                    for node in publisher[1]:
                        node_names.add(node)
                for subscriber in nodes[1]:  # subscribers
                    for node in subscriber[1]:
                        node_names.add(node)
                for service in nodes[2]:  # services
                    for node in service[1]:
                        node_names.add(node)
                return list(node_names)
            else:
                raise BridgeConnectionError(f"Failed to get system state: {msg}")
        except Exception as e:
            raise BridgeConnectionError(f"Failed to discover ROS nodes: {str(e)}")

    def discover_ros_topics(self) -> List[Dict[str, Any]]:
        """
        Discover all native ROS topics.

        Returns:
            List[Dict]: List of topic information dictionaries
        """
        if self._master is None:
            self.connect()

        try:
            code, msg, nodes = self._master.getSystemState("/")
            if code == 1:
                topics = []
                # Process publishers
                for publisher in nodes[0]:  # publishers
                    topic_name = publisher[0]
                    topic_type = publisher[1] if publisher[1] else "unknown"
                    topics.append(
                        {
                            "name": topic_name,
                            "type": topic_type,
                            "publishers": publisher[1],
                            "subscribers": [],
                        }
                    )
                return topics
            else:
                raise BridgeConnectionError(f"Failed to get system state: {msg}")
        except Exception as e:
            raise BridgeConnectionError(f"Failed to discover ROS topics: {str(e)}")

    def discover_ros_services(self) -> List[Dict[str, Any]]:
        """
        Discover all native ROS services.

        Returns:
            List[Dict]: List of service information dictionaries
        """
        if self._master is None:
            self.connect()

        try:
            code, msg, nodes = self._master.getSystemState("/")
            if code == 1:
                services = []
                # Process services
                for service in nodes[2]:  # services
                    service_name = service[0]
                    service_providers = service[1]
                    services.append(
                        {
                            "name": service_name,
                            "providers": service_providers,
                        }
                    )
                return services
            else:
                raise BridgeConnectionError(f"Failed to get system state: {msg}")
        except Exception as e:
            raise BridgeConnectionError(f"Failed to discover ROS services: {str(e)}")
