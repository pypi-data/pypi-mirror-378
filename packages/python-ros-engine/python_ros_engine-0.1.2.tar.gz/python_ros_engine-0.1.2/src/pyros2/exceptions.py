"""
Custom exceptions for the Python ROS engine.
"""


class PyROSException(Exception):
    """
    Base exception class for Python ROS engine.
    """

    pass


class NodeNotInitializedError(PyROSException):
    """
    Raised when trying to use a node that hasn't been initialized.
    """

    pass


class InvalidTopicNameError(PyROSException):
    """
    Raised when a topic name is invalid.
    """

    pass


class InvalidServiceNameError(PyROSException):
    """
    Raised when a service name is invalid.
    """

    pass


class ParameterNotDeclaredError(PyROSException):
    """
    Raised when trying to access a parameter that hasn't been declared.
    """

    pass


class ParameterAlreadyDeclaredError(PyROSException):
    """
    Raised when trying to declare a parameter that's already declared.
    """

    pass


class InvalidParameterTypeError(PyROSException):
    """
    Raised when a parameter type is invalid.
    """

    pass


class BridgeConnectionError(PyROSException):
    """
    Raised when there's an error connecting to the ROS bridge.
    """

    pass


class TopicNotFoundError(PyROSException):
    """
    Raised when a topic is not found during discovery.
    """

    pass


class ServiceNotFoundError(PyROSException):
    """
    Raised when a service is not found during discovery.
    """

    pass
