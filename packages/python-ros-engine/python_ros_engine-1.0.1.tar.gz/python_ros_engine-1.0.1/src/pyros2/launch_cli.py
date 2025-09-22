#!/usr/bin/env python3
"""Command-line interface for launching ROS nodes using the Python ROS engine."""

import argparse
import importlib
import os
import sys


def load_launch_file(file_path: str):
    """
    Load a launch description from a Python file.

    Args:
        file_path: Path to the launch file

    Returns:
        LaunchDescription object
    """
    # Add the directory containing the file to sys.path
    directory = os.path.dirname(file_path)
    if directory not in sys.path:
        sys.path.insert(0, directory)

    # Import the module
    module_name = os.path.basename(file_path).replace(".py", "")
    module = importlib.import_module(module_name)

    # Get the launch description
    if hasattr(module, "launch_description"):
        return module.launch_description
    elif hasattr(module, "generate_launch_description"):
        return module.generate_launch_description()
    else:
        raise ValueError(
            f"Launch file {file_path} must define either 'launch_description' "
            f"or 'generate_launch_description' function"
        )


def main():
    """Run the launch CLI."""
    parser = argparse.ArgumentParser(
        description="Launch ROS nodes using Python ROS engine"
    )
    parser.add_argument("launch_file", help="Path to the launch file")
    parser.add_argument(
        "--status", action="store_true", help="Print system status and exit"
    )

    args = parser.parse_args()

    try:
        # Load the launch description
        launch_description = load_launch_file(args.launch_file)

        # Execute the launch description to get the launch system
        launch_system = launch_description.execute()

        if args.status:
            # Print system status and exit
            launch_system.print_system_status()
        else:
            # Start the launch system
            launch_system.start()

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
