"""
Discovery implementation for the Python ROS engine.
"""

from typing import List

from .publisher import Publisher
from .service import Service


class Discovery:
    """
    Discovery mechanisms for topics and services.
    """

    @staticmethod
    def get_all_topics() -> List[str]:
        """
        Get all available topics.

        Returns:
            List[str]: List of all topic names
        """
        return list(Publisher._topic_registry.keys())

    @staticmethod
    def get_all_services() -> List[str]:
        """
        Get all available services.

        Returns:
            List[str]: List of all service names
        """
        return list(Service._service_registry.keys())

    @staticmethod
    def get_topic_types(topic_name: str) -> List[str]:
        """
        Get the types of a topic.

        Args:
            topic_name: Name of the topic

        Returns:
            List[str]: List of topic types
        """
        # In a real implementation, this would check all publishers/subscribers
        # For now, we'll just check if the topic exists
        if topic_name in Publisher._topic_registry:
            # Return a dummy type for now
            return ["std_msgs/String"]
        return []

    @staticmethod
    def get_service_types(service_name: str) -> List[str]:
        """
        Get the types of a service.

        Args:
            service_name: Name of the service

        Returns:
            List[str]: List of service types
        """
        # In a real implementation, this would check all service servers/clients
        # For now, we'll just check if the service exists
        if service_name in Service._service_registry:
            # Return a dummy type for now
            return ["example_interfaces/AddTwoInts"]
        return []

    @staticmethod
    def get_nodes() -> List[str]:
        """
        Get all available nodes.

        Returns:
            List[str]: List of all node names
        """
        # In a real implementation, this would discover all nodes in the network
        # For now, we'll return an empty list
        return []
