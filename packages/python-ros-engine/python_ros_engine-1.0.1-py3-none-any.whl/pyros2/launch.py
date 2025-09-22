"""Launch system implementation for the Python ROS engine."""

import importlib
import sys
import time
from typing import Any, Callable, Dict, List

from .discovery import Discovery
from .node import Node


class LaunchSystem:
    """Launch system for managing multiple nodes and providing system status.

    This class manages multiple ROS nodes and provides system status information.
    """

    def __init__(self):
        """Initialize the launch system."""
        self.nodes: Dict[str, Node] = {}
        self.running = False

    def add_node(self, node_name: str, node_class: type, *args, **kwargs):
        """
        Add a node to the launch system.

        Args:
            node_name: Name to register the node under
            node_class: The node class to instantiate
            *args: Positional arguments for node initialization
            **kwargs: Keyword arguments for node initialization
        """
        if node_name in self.nodes:
            raise ValueError(f"Node '{node_name}' already exists in launch system")

        node = node_class(*args, **kwargs)
        self.nodes[node_name] = node

    def add_node_from_file(
        self, node_name: str, file_path: str, class_name: str, *args, **kwargs
    ):
        """
        Add a node to the launch system from a Python file.

        Args:
            node_name: Name to register the node under
            file_path: Path to the Python file containing the node class
            class_name: Name of the node class in the file
            *args: Positional arguments for node initialization
            **kwargs: Keyword arguments for node initialization
        """
        if node_name in self.nodes:
            raise ValueError(f"Node '{node_name}' already exists in launch system")

        # Add the directory containing the file to sys.path
        import os

        directory = os.path.dirname(file_path)
        if directory not in sys.path:
            sys.path.insert(0, directory)

        # Import the module
        module_name = os.path.basename(file_path).replace(".py", "")
        module = importlib.import_module(module_name)

        # Get the class
        node_class = getattr(module, class_name)

        # Create and add the node
        node = node_class(*args, **kwargs)
        self.nodes[node_name] = node

    def remove_node(self, node_name: str):
        """
        Remove a node from the launch system.

        Args:
            node_name: Name of the node to remove
        """
        if node_name in self.nodes:
            node = self.nodes[node_name]
            node.destroy_node()
            del self.nodes[node_name]

    def start(self):
        """Start all nodes in the launch system."""
        if self.running:
            print("Launch system is already running")
            return

        print("Starting launch system...")
        print(f"Launching {len(self.nodes)} nodes:")
        for node_name, node in self.nodes.items():
            print(f"  - {node_name}")

        self.running = True

        # In a real implementation, we would start each node in its own thread
        # For now, we'll just indicate that the nodes are running
        try:
            while self.running:
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\nShutting down launch system...")
            self.shutdown()

    def shutdown(self):
        """Shutdown all nodes in the launch system."""
        self.running = False
        for node_name, node in self.nodes.items():
            print(f"Shutting down node '{node_name}'...")
            node.destroy_node()
        self.nodes.clear()
        print("Launch system shutdown complete.")

    def get_system_status(self) -> Dict[str, Any]:
        """
        Get the status of the entire system.

        Returns:
            Dict containing system status information
        """
        status = {
            "nodes": {},
            "topics": {},
            "services": {},
            "system_info": {
                "total_nodes": len(self.nodes),
                "running": self.running,
            },
        }

        # Get node information
        for node_name, node in self.nodes.items():
            status["nodes"][node_name] = {
                "name": node.node_name,
                "namespace": node.namespace,
                "publishers": len(node._publishers),
                "subscribers": len(node._subscribers),
                "services": len(node._services),
                "clients": len(node._clients),
                "parameters": len(node._parameters),
            }

        # Get topic information
        topics = Discovery.get_all_topics()
        for topic_name in topics:
            publishers_info = []
            subscribers_info = []

            # Collect publisher information for this topic
            for node_name, node in self.nodes.items():
                pubs_info = node.get_publishers_info_by_topic(topic_name)
                publishers_info.extend(pubs_info)

            # Collect subscriber information for this topic
            for node_name, node in self.nodes.items():
                subs_info = node.get_subscriptions_info_by_topic(topic_name)
                subscribers_info.extend(subs_info)

            status["topics"][topic_name] = {
                "name": topic_name,
                "types": Discovery.get_topic_types(topic_name),
                "publishers": publishers_info,
                "subscribers": subscribers_info,
            }

        # Get service information
        services = Discovery.get_all_services()
        for service_name in services:
            services_info = []
            clients_info = []

            # Collect service information for this service
            for node_name, node in self.nodes.items():
                for s_name, service in node._services.items():
                    if s_name == service_name:
                        services_info.append(
                            {
                                "node_name": node_name,
                                "service_name": service_name,
                                "service_type": (
                                    service.srv_type.__name__
                                    if hasattr(service.srv_type, "__name__")
                                    else str(service.srv_type)
                                ),
                            }
                        )

            # Collect client information for this service
            for node_name, node in self.nodes.items():
                for c_name, client in node._clients.items():
                    if c_name == service_name:
                        clients_info.append(
                            {
                                "node_name": node_name,
                                "service_name": service_name,
                                "service_type": (
                                    client.srv_type.__name__
                                    if hasattr(client.srv_type, "__name__")
                                    else str(client.srv_type)
                                ),
                            }
                        )

            status["services"][service_name] = {
                "name": service_name,
                "types": Discovery.get_service_types(service_name),
                "servers": services_info,
                "clients": clients_info,
            }

        return status

    def print_system_status(self):
        """Print the status of the entire system in a human-readable format."""
        status = self.get_system_status()

        print("=" * 50)
        print("ROS SYSTEM STATUS")
        print("=" * 50)

        # System info
        print(f"System Running: {status['system_info']['running']}")
        print(f"Total Nodes: {status['system_info']['total_nodes']}")
        print()

        # Node info
        if status["nodes"]:
            print("NODES:")
            print("-" * 30)
            for node_name, node_info in status["nodes"].items():
                print(f"  Name: {node_info['name']}")
                print(f"  Namespace: {node_info['namespace']}")
                print(f"  Publishers: {node_info['publishers']}")
                print(f"  Subscribers: {node_info['subscribers']}")
                print(f"  Services: {node_info['services']}")
                print(f"  Clients: {node_info['clients']}")
                print(f"  Parameters: {node_info['parameters']}")
                print()
        else:
            print("No nodes found.")
            print()

        # Topic info
        if status["topics"]:
            print("TOPICS:")
            print("-" * 30)
            for topic_name, topic_info in status["topics"].items():
                print(f"  Name: {topic_info['name']}")
                print(f"  Types: {topic_info['types']}")
                print(f"  Publishers: {len(topic_info['publishers'])}")
                for pub in topic_info["publishers"]:
                    print(f"    - {pub['node_name']}")
                print(f"  Subscribers: {len(topic_info['subscribers'])}")
                for sub in topic_info["subscribers"]:
                    print(f"    - {sub['node_name']}")
                print()
        else:
            print("No topics found.")
            print()

        # Service info
        if status["services"]:
            print("SERVICES:")
            print("-" * 30)
            for service_name, service_info in status["services"].items():
                print(f"  Name: {service_info['name']}")
                print(f"  Types: {service_info['types']}")
                print(f"  Servers: {len(service_info['servers'])}")
                for server in service_info["servers"]:
                    print(f"    - {server['node_name']}")
                print(f"  Clients: {len(service_info['clients'])}")
                for client in service_info["clients"]:
                    print(f"    - {client['node_name']}")
                print()
        else:
            print("No services found.")
            print()


class LaunchDescription:
    """Description of a launch system configuration."""

    def __init__(self, launch_system: LaunchSystem = None):
        """
        Initialize a launch description.

        Args:
            launch_system: Optional LaunchSystem to use
        """
        self.launch_system = launch_system or LaunchSystem()
        self.actions: List[Callable] = []

    def add_node(self, node_class: type, *args, **kwargs):
        """
        Add a node action to the launch description.

        Args:
            node_class: The node class to instantiate
            *args: Positional arguments for node initialization
            **kwargs: Keyword arguments for node initialization
        """

        def action():
            node = node_class(*args, **kwargs)
            self.launch_system.nodes[node.node_name] = node

        self.actions.append(action)

    def add_node_from_file(self, file_path: str, class_name: str, *args, **kwargs):
        """
        Add a node action from a Python file to the launch description.

        Args:
            file_path: Path to the Python file containing the node class
            class_name: Name of the node class in the file
            *args: Positional arguments for node initialization
            **kwargs: Keyword arguments for node initialization
        """

        def action():
            self.launch_system.add_node_from_file(
                f"{class_name}_{len(self.launch_system.nodes)}",
                file_path,
                class_name,
                *args,
                **kwargs,
            )

        self.actions.append(action)

    def execute(self):
        """Execute all actions in the launch description."""
        for action in self.actions:
            action()
        return self.launch_system
