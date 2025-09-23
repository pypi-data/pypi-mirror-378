import asyncio
import contextlib
import functools
import logging
import uuid
from collections import deque
from collections.abc import (
    AsyncIterator,
    Awaitable,
    Callable,
    Collection,
    Iterable,
    Sequence,
)
from functools import partial
from typing import Any, Protocol, cast

import grpc
import grpc.aio
from google.protobuf.struct_pb2 import Struct  # type: ignore[import-untyped]
from langchain_core.messages import BaseMessage, BaseMessageChunk
from langchain_core.runnables import RunnableConfig, RunnableSequence
from langgraph._internal._config import patch_config
from langgraph._internal._constants import (
    CONFIG_KEY_READ,
    CONFIG_KEY_SEND,
    CONFIG_KEY_TASK_ID,
    INTERRUPT,
)
from langgraph.checkpoint.base import Checkpoint
from langgraph.errors import GraphBubbleUp, GraphInterrupt, InvalidUpdateError
from langgraph.graph.state import Pregel, PregelNode
from langgraph.pregel._algo import (
    PregelTaskWrites,
    _scratchpad,
    apply_writes,
    local_read,
)
from langgraph.pregel._checkpoint import channels_from_checkpoint
from langgraph.pregel._retry import arun_with_retry
from langgraph.store.base import BaseStore
from langgraph.types import PregelExecutableTask
from langgraph_distributed_utils.conversion.channel import (
    channels_from_proto,
    channels_to_proto,
)
from langgraph_distributed_utils.conversion.checkpoint import (
    checkpoint_from_proto,
    checkpoint_to_proto,
)
from langgraph_distributed_utils.conversion.config import config_from_proto
from langgraph_distributed_utils.conversion.exception import exception_to_proto
from langgraph_distributed_utils.conversion.graph import graph_to_proto
from langgraph_distributed_utils.conversion.task import (
    pregel_executable_task_from_proto,
    task_writes_from_proto,
    task_writes_to_proto,
)
from langgraph_distributed_utils.conversion.value import value_from_proto
from langgraph_distributed_utils.proto import executor_pb2, executor_pb2_grpc, types_pb2
from langgraph_distributed_utils.proto.runtime_pb2_grpc import LangGraphRuntimeStub
from langgraph_distributed_utils.runtime_client.patch import (
    patch_pregel,
    var_child_runnable_config,
)

from langgraph_executor.stream_utils import ExecutorStreamHandler


class Logger(Protocol):
    def debug(self, msg: str, *args: Any, **kwargs: Any) -> None: ...
    def info(self, msg: str, *args: Any, **kwargs: Any) -> None: ...
    def warning(self, msg: str, *args: Any, **kwargs: Any) -> None: ...
    def error(self, msg: str, *args: Any, **kwargs: Any) -> None: ...
    def exception(self, msg: str, *args: Any, **kwargs: Any) -> None: ...
    def critical(self, msg: str, *args: Any, **kwargs: Any) -> None: ...


LOGGER = logging.getLogger(__name__)
SENTINEL = cast(executor_pb2.ExecuteTaskResponse, object())
GetGraph = Callable[
    [str, RunnableConfig], contextlib.AbstractAsyncContextManager[Pregel]
]


class LangGraphExecutorServicer(executor_pb2_grpc.LangGraphExecutorServicer):
    """gRPC servicer for LangGraph runtime execution operations."""

    def __init__(
        self,
        graphs: Collection[str],
        *,
        subgraph_map: dict[str, str],
        get_graph: GetGraph,
        runtime_channel: grpc.Channel | None = None,
        logger: Logger | None = None,
        on_message: (
            Callable[
                [
                    BaseMessageChunk,
                    dict[str, Any],
                ],
                None,
            ]
            | None
        ) = None,
        on_custom: Callable[[Any], None] | None = None,
        get_store: Callable[[], Awaitable[BaseStore]] | None = None,
    ):
        """Initialize the servicer with compiled graphs.

        Args:
            graphs: Dictionary mapping graph names to compiled graphs
            subgraph_map: Dictionary mapping subgraph names to parent graph names
            get_graph: Function to get a graph by name
            logger: Optional logger

        """
        self.logger = logger or LOGGER
        self.graphs = set(graphs)
        self.graph_names = sorted(self.graphs)
        self.subgraph_map = subgraph_map
        self.get_graph = get_graph
        self.runtime_channel = runtime_channel
        self.runtime_client: LangGraphRuntimeStub | None = (
            LangGraphRuntimeStub(runtime_channel)
            if runtime_channel is not None
            else None
        )
        if self.runtime_client is not None:
            patch_pregel(self.runtime_client, self.logger)
        self._graph_definition_cache: dict[str, executor_pb2.GetGraphResponse] = {}
        self.on_message = on_message
        self.on_custom = on_custom
        self.get_store = get_store

    async def ListGraphs(
        self, request: executor_pb2.ListGraphsRequest, context: grpc.aio.ServicerContext
    ) -> executor_pb2.ListGraphsResponse:  # type: ignore[name-defined]
        """List available graphs."""
        return executor_pb2.ListGraphsResponse(
            graph_names=self.graph_names,
        )

    async def GetGraph(
        self, request: executor_pb2.GetGraphRequest, context: grpc.aio.ServicerContext
    ) -> executor_pb2.GetGraphResponse:  # type: ignore[name-defined]
        """Get graph definition."""
        try:
            self.logger.debug(
                "GetGraph called", extra={"graph_name": request.graph_name}
            )
            graph_name: str = request.graph_name
            return await self._get_graph_definition(graph_name)

        except Exception as e:
            self.logger.error(f"GetGraph Error: {e}", exc_info=True)
            await context.abort(grpc.StatusCode.INTERNAL, str(e))

    async def _get_graph_definition(self, name: str) -> executor_pb2.GetGraphResponse:
        if (resp := self._graph_definition_cache.get(name)) is not None:
            return resp
        async with self.get_graph(name, RunnableConfig()) as graph:
            graph_definition = graph_to_proto(graph, name=name)

            resp = executor_pb2.GetGraphResponse(
                graph_definition=graph_definition,
                parent_name=self.subgraph_map.get(name, None),
                checkpointer=graph.checkpointer is not None,
            )
            self._graph_definition_cache[name] = resp
            return resp

    async def GetAllGraphs(
        self,
        request: executor_pb2.GetAllGraphsRequest,
        context: grpc.aio.ServicerContext,
    ) -> AsyncIterator[executor_pb2.GetGraphResponse]:
        try:
            self.logger.debug("GetAllGraphs called")
            for name in self.graph_names:
                yield await self._get_graph_definition(name)

        except Exception as e:
            self.logger.error(f"GetAllGraphs Error: {e}", exc_info=True)
            await context.abort(grpc.StatusCode.INTERNAL, str(e))

    async def ChannelsFromCheckpoint(
        self,
        request: executor_pb2.ChannelsFromCheckpointRequest,
        context: grpc.aio.ServicerContext,
    ) -> executor_pb2.ChannelsFromCheckpointResponse:  # type: ignore[name-defined]
        try:
            self.logger.debug(
                "ChannelsFromCheckpoint called",
                extra={
                    "graph_name": request.graph_name,
                    "specs": request.specs,
                    "checkpoint_channel_values": request.checkpoint_channel_values,
                },
            )
            async with self.get_graph(request.graph_name, RunnableConfig()) as graph:
                # reconstruct specs
                specs, _ = channels_from_proto(
                    request.specs.channels,
                    graph,
                )

                # initialize channels from specs and checkpoint channel values
                checkpoint_dummy = Checkpoint(  # type: ignore[typeddict-item]
                    channel_values={
                        k: value_from_proto(v)
                        for k, v in request.checkpoint_channel_values.items()
                    },
                )
                channels, _ = channels_from_checkpoint(specs, checkpoint_dummy)

                # channels to pb
                channels = channels_to_proto(channels)

                return executor_pb2.ChannelsFromCheckpointResponse(channels=channels)

        except Exception as e:
            self.logger.error(f"ChannelsFromCheckpoint Error: {e}", exc_info=True)
            await context.abort(grpc.StatusCode.INTERNAL, str(e))

    async def ExecuteTask(
        self,
        request_iterator: AsyncIterator[executor_pb2.ExecuteTaskRequest],  # type: ignore[name-defined]
        context: grpc.aio.ServicerContext,
    ) -> AsyncIterator[executor_pb2.ExecuteTaskResponse]:  # type: ignore[name-defined]
        try:
            request = await _get_init_request(request_iterator)
            self.logger.debug(
                "ExecuteTask called",
                extra={
                    "graph_name": request.graph_name,
                    "task": request.task,
                    "stream_modes": request.stream_modes,
                },
            )

            task_proto: types_pb2.Task = request.task
            config_proto: types_pb2.RunnableConfig = task_proto.config
            step = request.step
            stop = request.stop
            channels_proto: types_pb2.Channels = request.channels

            config = config_from_proto(config_proto)
            store = await self.get_store() if self.get_store is not None else None
            async with self.get_graph(request.graph_name, config) as graph:
                node = get_node(task_proto.name, graph, request.graph_name)

                stream_messages = "messages" in request.stream_modes
                stream_custom = "custom" in request.stream_modes

                stream_queue = asyncio.Queue()

                custom_stream_writer = (
                    _create_custom_stream_writer(
                        stream_queue, self.logger, on_custom=self.on_custom
                    )
                    if stream_custom
                    else None
                )

                # TODO should we put config here?
                task = pregel_executable_task_from_proto(
                    task_proto,
                    step,
                    stop,
                    channels_proto,
                    graph,
                    node,
                    custom_stream_writer=custom_stream_writer,
                    store=store,
                )
                if stream_messages:
                    # Create and inject callback handler
                    stream_handler = ExecutorStreamHandler(
                        functools.partial(
                            stream_callback,
                            logger=self.logger,
                            stream_queue=stream_queue,
                            on_message=self.on_message,
                        ),
                        task.id,
                    )

                    # Add handler to task config callbacks
                    if "callbacks" not in task.config:
                        task.config["callbacks"] = []
                    task.config["callbacks"].append(stream_handler)  # type: ignore[union-attr]

                # Execute task, catching interrupts
                # Check cache if task has cache key - send request to Go orchestrator
                should_execute = True
                if task.cache_key:
                    self.logger.debug(
                        f"Task {task.id} has cache key, sending cache check request to Go",
                    )

                    # Send cache check request to Go runtime
                    cache_check_request = executor_pb2.CacheCheckRequest(
                        cache_namespace=list(task.cache_key.ns),
                        cache_key=task.cache_key.key,
                        ttl=task.cache_key.ttl,
                    )

                    yield executor_pb2.ExecuteTaskResponse(
                        cache_check_request=cache_check_request,
                    )

                    # Wait for Go's response via the bidirectional stream
                    try:
                        cache_response_request = next(request_iterator)  # type: ignore[invalid-argument-type]
                        if hasattr(cache_response_request, "cache_check_response"):
                            cache_response = cache_response_request.cache_check_response
                            should_execute = not cache_response.cache_hit
                            self.logger.debug(
                                f"Received cache response for task {task.id}: cache_hit={cache_response.cache_hit}",
                            )
                        else:
                            self.logger.warning(
                                f"Expected cache_check_response for task {task.id}, got unexpected message type",
                            )
                            should_execute = (
                                True  # Default to execution if unexpected response
                            )
                    except StopIteration:
                        self.logger.warning(
                            f"No cache response received for task {task.id}, defaulting to execution",
                        )
                        should_execute = True  # Default to execution if no response

                # TODO patch retry policy
                # TODO configurable to deal with _call and the functional api
                exception_pb = None
                if should_execute:
                    runner_task = asyncio.create_task(
                        _run_task(task, logger=self.logger, stream_queue=stream_queue)
                    )
                    # Drain the queue and stream responses to client
                    while True:
                        item = await stream_queue.get()
                        if item is SENTINEL:
                            break
                        yield item
                    exception_pb = await runner_task

                # Ensure the final chat messages are emitted (if any)
                for message in _extract_output_messages(
                    task.writes, meta=task.config.get("metadata", {})
                ):
                    yield executor_pb2.ExecuteTaskResponse(
                        message_or_message_chunk=message
                    )

                # Final task result
                writes_proto = task_writes_to_proto(task.writes)
                yield executor_pb2.ExecuteTaskResponse(
                    task_result=executor_pb2.TaskResult(
                        error=exception_pb, writes=writes_proto
                    )
                )

        except Exception as e:
            self.logger.exception(f"ExecuteTask error: {e}")
            await context.abort(grpc.StatusCode.INTERNAL, str(e))

    async def ApplyWrites(
        self,
        request: executor_pb2.ApplyWritesRequest,
        context: grpc.aio.ServicerContext,
    ) -> executor_pb2.ApplyWritesResponse:  # type: ignore[name-defined]
        # get graph
        try:
            self.logger.debug(
                "ApplyWrites called",
                extra={
                    "graph_name": request.graph_name,
                    "tasks": request.tasks,
                    "channels": request.channels,
                    "checkpoint": request.checkpoint,
                },
            )
            async with self.get_graph(request.graph_name, RunnableConfig()) as graph:
                channels, _ = channels_from_proto(
                    request.channels.channels,
                    graph,
                )
                checkpoint = checkpoint_from_proto(request.checkpoint)
                tasks = task_writes_from_proto(request.tasks)

                # apply writes
                updated_channel_names_set = apply_writes(
                    checkpoint,
                    channels,
                    tasks,
                    lambda *args: request.next_version,
                    graph.trigger_to_nodes,
                )
                updated_channel_names = list(updated_channel_names_set)

                # Reconstruct protos
                updated_channels = channels_to_proto(channels)
                checkpoint_proto = checkpoint_to_proto(checkpoint)

                # Respond with updates
                return executor_pb2.ApplyWritesResponse(
                    updates=types_pb2.Updates(
                        checkpoint=checkpoint_proto,
                        updated_channels=updated_channel_names,
                        channels=updated_channels,
                    ),
                )

        except Exception as e:
            self.logger.exception(f"ApplyWrites error: {e}")
            await context.abort(grpc.StatusCode.INTERNAL, str(e))

    async def StateUpdate(
        self,
        request: executor_pb2.StateUpdateRequest,
        context: grpc.aio.ServicerContext,
    ) -> executor_pb2.TaskResult | None:
        try:
            self.logger.debug(
                "StateUpdate called",
                extra={
                    "graph_name": request.graph_name,
                    "node_name": request.node_name,
                    "task_id": request.task_id,
                    "values": request.values,
                },
            )
            async with self.get_graph(request.graph_name, RunnableConfig()) as graph:
                config = config_from_proto(request.config)
                channels, managed = channels_from_proto(
                    request.channels.channels,
                    graph,
                )
                writes: deque[tuple[str, Any]] = deque()
                writers = graph.nodes[request.node_name].flat_writers
                if not writers:
                    raise InvalidUpdateError(f"Node {request.node_name} has no writers")
                task = PregelTaskWrites((), request.node_name, writes, [INTERRUPT])
                task_id = request.task_id

                run = RunnableSequence(*writers) if len(writers) > 1 else writers[0]

                input = value_from_proto(request.values)

                run.invoke(
                    input,
                    patch_config(
                        config,
                        run_name=graph.name + "UpdateState",
                        configurable={
                            # deque.extend is thread-safe
                            CONFIG_KEY_SEND: writes.extend,
                            CONFIG_KEY_TASK_ID: task_id,
                            CONFIG_KEY_READ: partial(
                                local_read,
                                _scratchpad(
                                    None,
                                    [],
                                    task_id,
                                    "",
                                    None,
                                    request.step,
                                    request.step + 2,
                                ),
                                channels,
                                managed,
                                task,
                            ),
                        },
                    ),
                )

                return executor_pb2.TaskResult(writes=task_writes_to_proto(task.writes))

        except Exception as e:
            self.logger.exception(f"StateUpdate error: {e}")
            await context.abort(grpc.StatusCode.INTERNAL, str(e))

    async def GenerateCacheKey(
        self,
        request: executor_pb2.GenerateCacheKeyRequest,
        context: grpc.aio.ServicerContext,
    ) -> executor_pb2.GenerateCacheKeyResponse:
        """Generate cache key for a node execution"""
        raise NotImplementedError("GenerateCacheKey not implemented")


# Helpers


async def _run_task(
    task: PregelExecutableTask,
    *,
    logger: Logger,
    stream_queue: asyncio.Queue[executor_pb2.ExecuteTaskResponse],
) -> types_pb2.ExecutorError | None:
    # Set config
    var_child_runnable_config.set(task.config)
    try:
        await arun_with_retry(
            task,
            retry_policy=None,
        )

    except Exception as e:
        if isinstance(e, GraphBubbleUp | GraphInterrupt):
            logger.info(f"Interrupt in task {task.id}: {type(e)}({e})")
        else:
            logger.exception(
                f"Exception running task {task.id}: {type(e)}({e})\nTask: {task}\n\n",
                exc_info=True,
            )
        return exception_to_proto(e)
    finally:
        await stream_queue.put(SENTINEL)


def stream_callback(
    message: BaseMessageChunk,
    metadata: dict[str, Any],
    *,
    logger: Logger,
    stream_queue: asyncio.Queue[executor_pb2.ExecuteTaskResponse],
    on_message: Callable[[BaseMessageChunk, dict[str, Any]], None] | None = None,
):
    """Callback to capture stream chunks and queue them."""
    try:
        if on_message is not None:
            on_message(message, metadata)
        stream_queue.put_nowait(
            executor_pb2.ExecuteTaskResponse(
                message_or_message_chunk=_extract_output_message(message, metadata)
            )
        )
    except Exception as e:
        logger.warning(f"Failed to create stream chunk: {e}", exc_info=True)


def _create_custom_stream_writer(
    stream_queue: asyncio.Queue[Any],
    logger: Logger,
    *,
    on_custom: Callable[[Any], None] | None = None,
):
    """Create a proper stream_writer function for custom mode (like langgraph does)."""

    def stream_writer(content):
        """Custom stream writer that creates CustomStreamEvent messages."""
        try:
            if on_custom is not None:
                on_custom(content)
            # Create payload struct (like langgraph does)
            payload = Struct()
            if isinstance(content, str):
                payload.update({"content": content})
            elif isinstance(content, dict):
                payload.update(content)
            else:
                payload.update({"content": str(content)})

            # Create CustomStreamEvent
            custom_event = executor_pb2.CustomStreamEvent(payload=payload)
            custom_event_response = executor_pb2.ExecuteTaskResponse(
                custom_stream_event=custom_event
            )
            stream_queue.put_nowait(custom_event_response)

        except Exception as e:
            logger.warning(f"Failed to create custom stream event: {e}", exc_info=True)

    return stream_writer


def _extract_output_messages(
    writes: Sequence[Any], meta: dict[str, Any] | None = None
) -> Iterable[types_pb2.Message]:  # type: ignore[name-defined]
    for write in writes:
        # Not sure this check is right
        if isinstance(write[1], BaseMessage):
            yield _extract_output_message(write[1], meta)
        elif isinstance(write[1], Sequence):
            for w in write[1]:
                if isinstance(w, BaseMessage):
                    yield _extract_output_message(w, meta)


def _extract_output_message(
    write: Any, meta: dict[str, Any] | None = None
) -> types_pb2.Message:  # type: ignore[name-defined]
    message = Struct()
    kind = getattr(write, "type", None)
    message_fields = {}
    if isinstance(kind, str):
        lowerkind = kind.lower()
        if lowerkind.startswith("ai"):
            message_fields.update(
                {
                    "usage_metadata": getattr(write, "usage_metadata", {}),
                    "invalid_tool_calls": getattr(write, "invalid_tool_calls", []),
                    "tool_calls": getattr(write, "tool_calls", []),
                    "tool_call_chunks": getattr(write, "tool_call_chunks", []),
                    "response_metadata": getattr(write, "response_metadata", {}),
                }
            )
        elif lowerkind.startswith("tool"):
            message_fields.update(
                {
                    "tool_call_id": getattr(write, "tool_call_id", ""),
                }
            )
    message.update(
        {
            "is_streaming_chunk": isinstance(write, BaseMessageChunk),
            "message": {
                "id": getattr(write, "id", None) or uuid.uuid4().hex,
                "example": getattr(write, "example", False),
                "name": getattr(write, "name", None),
                "type": kind,
                "content": str(getattr(write, "content", "") or ""),
                "additional_kwargs": getattr(write, "additional_kwargs", {}),
                **message_fields,
            },
            "metadata": meta or {},
        }
    )

    return types_pb2.Message(payload=message)


async def _get_init_request(
    request_iterator: AsyncIterator[executor_pb2.ExecuteTaskInit],
) -> executor_pb2.ExecuteTaskInit:
    request = await anext(request_iterator)

    if not hasattr(request, "init"):
        raise ValueError("First message must be init")

    return request.init


def get_graph(
    graph_name: str,
    graphs: dict[str, Pregel],
) -> Pregel:
    if graph_name not in graphs:
        raise ValueError(f"Graph {graph_name} not supported")
    return graphs[graph_name]


def get_node(node_name: str, graph: Pregel, graph_name: str) -> PregelNode:
    if node_name not in graph.nodes:
        raise ValueError(f"Node {node_name} not found in graph {graph_name}")
    return graph.nodes[node_name]
