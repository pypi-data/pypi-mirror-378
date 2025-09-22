from __future__ import annotations

import asyncio
import contextlib
import datetime
import logging
from collections.abc import AsyncIterator, Generator
from typing import TYPE_CHECKING, Any, TypeVar
from uuid import uuid4

from injectq import InjectQ

from pyagenity.checkpointer.base_checkpointer import BaseCheckpointer
from pyagenity.publisher.base_publisher import BasePublisher
from pyagenity.state import AgentState
from pyagenity.store.base_store import BaseStore
from pyagenity.utils import (
    ResponseGranularity,
)
from pyagenity.utils.background_task_manager import BackgroundTaskManager
from pyagenity.utils.message import Message

from .utils.invoke_handler import InvokeHandler
from .utils.stream_handler import StreamHandler


if TYPE_CHECKING:
    from .state_graph import StateGraph


StateT = TypeVar("StateT", bound=AgentState)

logger = logging.getLogger(__name__)


class CompiledGraph[StateT: AgentState]:
    """A compiled graph ready for execution.

    Generic over state types to support custom AgentState subclasses.
    """

    def __init__(
        self,
        state: StateT,
        checkpointer: BaseCheckpointer[StateT] | None,
        publisher: BasePublisher | None,
        store: BaseStore[StateT] | None,
        state_graph: StateGraph[StateT],
        interrupt_before: list[str],
        interrupt_after: list[str],
        task_manager: BackgroundTaskManager,
    ):
        logger.info(
            f"Initializing CompiledGraph with nodes: {list(state_graph.nodes.keys())}",
        )

        # Save initial state
        self._state = state

        # create handlers
        self._invoke_handler: InvokeHandler[StateT] = InvokeHandler[StateT](
            nodes=state_graph.nodes,  # type: ignore
            edges=state_graph.edges,  # type: ignore
        )
        self._stream_handler: StreamHandler[StateT] = StreamHandler[StateT](
            nodes=state_graph.nodes,  # type: ignore
            edges=state_graph.edges,  # type: ignore
        )

        self._checkpointer: BaseCheckpointer[StateT] | None = checkpointer
        self._publisher: BasePublisher | None = publisher
        self._store: BaseStore[StateT] | None = store
        self._state_graph: StateGraph[StateT] = state_graph
        self._interrupt_before: list[str] = interrupt_before
        self._interrupt_after: list[str] = interrupt_after
        # generate task manager
        self._task_manager = task_manager

    def _prepare_config(
        self,
        config: dict[str, Any] | None,
        is_stream: bool = False,
    ) -> dict[str, Any]:
        cfg = config or {}
        if "is_stream" not in cfg:
            cfg["is_stream"] = is_stream
        if "user_id" not in cfg:
            cfg["user_id"] = "test-user-id"  # mock user id
        if "run_id" not in cfg:
            cfg["run_id"] = InjectQ.get_instance().try_get("generated_id") or str(uuid4())

        if "timestamp" not in cfg:
            cfg["timestamp"] = datetime.datetime.now().isoformat()

        return cfg

    def invoke(
        self,
        input_data: dict[str, Any],
        config: dict[str, Any] | None = None,
        response_granularity: ResponseGranularity = ResponseGranularity.LOW,
    ) -> dict[str, Any]:
        """Execute the graph synchronously.

        Auto-detects whether to start fresh execution or resume from interrupted state.

        Args:
            input_data: Input dict
            config: Configuration dictionary

        Returns:
            Final state dict and messages
        """
        logger.info(
            "Starting synchronous graph execution with %d input keys, granularity=%s",
            len(input_data) if input_data else 0,
            response_granularity,
        )
        logger.debug("Input data keys: %s", list(input_data.keys()) if input_data else [])
        # Async Will Handle Event Publish

        try:
            result = asyncio.run(self.ainvoke(input_data, config, response_granularity))
            logger.info("Synchronous graph execution completed successfully")
            return result
        except Exception as e:
            logger.exception("Synchronous graph execution failed: %s", e)
            raise

    async def ainvoke(
        self,
        input_data: dict[str, Any],
        config: dict[str, Any] | None = None,
        response_granularity: ResponseGranularity = ResponseGranularity.LOW,
    ) -> dict[str, Any]:
        """Execute the graph asynchronously.

        Auto-detects whether to start fresh execution or resume from interrupted state
        based on the AgentState's execution metadata.

        Args:
            input_data: Input dict with 'messages' key (for new execution) or
                       additional data for resuming
            config: Configuration dictionary
            response_granularity: Response parsing granularity

        Returns:
            Response dict based on granularity
        """
        cfg = self._prepare_config(config, is_stream=False)

        return await self._invoke_handler.invoke(
            input_data,
            cfg,
            self._state,
            response_granularity,
        )

    def stream(
        self,
        input_data: dict[str, Any],
        config: dict[str, Any] | None = None,
        response_granularity: ResponseGranularity = ResponseGranularity.LOW,
    ) -> Generator[Message]:
        """Execute the graph synchronously with streaming support.

        Yields Message objects containing incremental responses.
        If nodes return streaming responses, yields them directly.
        If nodes return complete responses, simulates streaming by chunking.

        Args:
            input_data: Input dict
            config: Configuration dictionary
            response_granularity: Response parsing granularity

        Yields:
            Message objects with incremental content
        """

        # For sync streaming, we'll use asyncio.run to handle the async implementation
        async def _async_stream():
            async for chunk in self.astream(input_data, config, response_granularity):
                yield chunk

        # Convert async generator to sync iteration with a dedicated event loop
        gen = _async_stream()
        loop = asyncio.new_event_loop()
        policy = asyncio.get_event_loop_policy()
        try:
            previous_loop = policy.get_event_loop()
        except Exception:
            previous_loop = None
        asyncio.set_event_loop(loop)
        logger.info("Synchronous streaming started")

        try:
            while True:
                try:
                    chunk = loop.run_until_complete(gen.__anext__())
                    yield chunk
                except StopAsyncIteration:
                    break
        finally:
            # Attempt to close the async generator cleanly
            with contextlib.suppress(Exception):
                loop.run_until_complete(gen.aclose())  # type: ignore[attr-defined]
            # Restore previous loop if any, then close created loop
            try:
                if previous_loop is not None:
                    asyncio.set_event_loop(previous_loop)
            finally:
                loop.close()
        logger.info("Synchronous streaming completed")

    async def astream(
        self,
        input_data: dict[str, Any],
        config: dict[str, Any] | None = None,
        response_granularity: ResponseGranularity = ResponseGranularity.LOW,
    ) -> AsyncIterator[Message]:
        """Execute the graph asynchronously with streaming support.

        Yields Message objects containing incremental responses.
        If nodes return streaming responses, yields them directly.
        If nodes return complete responses, simulates streaming by chunking.

        Args:
            input_data: Input dict
            config: Configuration dictionary
            response_granularity: Response parsing granularity

        Yields:
            Message objects with incremental content
        """

        cfg = self._prepare_config(config, is_stream=True)

        async for chunk in self._stream_handler.stream(
            input_data,
            cfg,
            self._state,
            response_granularity,
        ):
            yield chunk

    async def aclose(self) -> dict[str, str]:
        """Close the graph and release any resources."""
        # close checkpointer
        stats = {}
        try:
            if self._checkpointer:
                await self._checkpointer.arelease()
                logger.info("Checkpointer closed successfully")
                stats["checkpointer"] = "closed"
        except Exception as e:
            stats["checkpointer"] = f"error: {e}"
            logger.error(f"Error closing graph: {e}")

        # Close Publisher
        try:
            if self._publisher:
                await self._publisher.close()
                logger.info("Publisher closed successfully")
                stats["publisher"] = "closed"
        except Exception as e:
            stats["publisher"] = f"error: {e}"
            logger.error(f"Error closing publisher: {e}")

        # Close Store
        try:
            if self._store:
                await self._store.arelease()
                logger.info("Store closed successfully")
                stats["store"] = "closed"
        except Exception as e:
            stats["store"] = f"error: {e}"
            logger.error(f"Error closing store: {e}")

        # Wait for all background tasks to complete
        try:
            await self._task_manager.wait_for_all()
            logger.info("All background tasks completed successfully")
            stats["background_tasks"] = "completed"
        except Exception as e:
            stats["background_tasks"] = f"error: {e}"
            logger.error(f"Error waiting for background tasks: {e}")

        logger.info(f"Graph close stats: {stats}")
        # You can also return or process the stats as needed
        return stats

    def generate_graph(self) -> dict[str, Any]:
        """Generate the graph representation.

        Returns:
            A dictionary representing the graph structure.
        """
        graph = {
            "info": {},
            "nodes": [],
            "edges": [],
        }
        # Populate the graph with nodes and edges
        for node_name in self._state_graph.nodes:
            graph["nodes"].append(
                {
                    "id": str(uuid4()),
                    "name": node_name,
                }
            )

        for edge in self._state_graph.edges:
            graph["edges"].append(
                {
                    "id": str(uuid4()),
                    "source": edge.from_node,
                    "target": edge.to_node,
                }
            )

        # Add few more extra info
        graph["info"] = {
            "node_count": len(graph["nodes"]),
            "edge_count": len(graph["edges"]),
            "checkpointer": self._checkpointer is not None,
            "checkpointer_type": type(self._checkpointer).__name__ if self._checkpointer else None,
            "publisher": self._publisher is not None,
            "store": self._store is not None,
            "interrupt_before": self._interrupt_before,
            "interrupt_after": self._interrupt_after,
            "context_type": self._state_graph._context_manager.__class__.__name__,
            "id_generator": self._state_graph._id_generator.__class__.__name__,
            "id_type": self._state_graph._id_generator.id_type.value,
            "state_type": self._state.__class__.__name__,
            "state_fields": list(self._state.model_dump().keys()),
        }
        return graph
