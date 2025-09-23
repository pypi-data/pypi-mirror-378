from abc import ABC, abstractmethod
from typing import Any

from .events import EventModel


class BasePublisher(ABC):
    """
    Abstract base class for event publishers.

    This class defines the interface for publishing events. Subclasses should implement
    the `publish`, `close`, and `sync_close` methods to provide specific publishing logic.

    Example:
        >>> from pyagenity.publisher.base_publisher import BasePublisher
        >>> class MyPublisher(BasePublisher):
        ...     async def publish(self, event):
        ...         print(event)
        ...
        ...     def close(self):
        ...         pass
        ...
        ...     def sync_close(self):
        ...         pass
        >>> pub = MyPublisher({})
    """

    def __init__(self, config: dict[str, Any]):
        """
        Initialize the publisher with the given configuration.

        Args:
            config (dict[str, Any]): Configuration dictionary for the publisher.
        """
        self.config = config

    @abstractmethod
    async def publish(self, event: EventModel) -> Any:
        """
        Publish an event.

        Args:
            event (Event): The event to publish.

        Returns:
            Any: The result of the publish operation.
        """
        raise NotImplementedError

    @abstractmethod
    async def close(self):
        """
        Close the publisher and release any resources.

        This method should be overridden by subclasses to provide specific cleanup logic.
        It will be called externally.
        """
        raise NotImplementedError

    @abstractmethod
    def sync_close(self):
        """
        Close the publisher and release any resources (synchronous version).

        This method should be overridden by subclasses to provide specific cleanup logic.
        It will be called externally.
        """
        raise NotImplementedError
