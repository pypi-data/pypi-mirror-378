import asyncio
import logging
from collections.abc import Iterator, Sequence
from contextvars import ContextVar
from typing import Any

import grpc
import orjson
from google.protobuf.struct_pb2 import Struct
from langchain_core.runnables import RunnableConfig
from langgraph._internal._config import ensure_config
from langgraph.errors import (
    EmptyInputError,
    GraphBubbleUp,
    GraphInterrupt,
    GraphRecursionError,
    ParentCommand,
)
from langgraph.pregel import Pregel
from langgraph.runtime import get_runtime
from langgraph.types import (
    All,
    Command,
    Durability,
    Interrupt,
    StateSnapshot,
    StateUpdate,
    StreamMode,
)
from langgraph.typing import ContextT, InputT
from pydantic import ValidationError

from langgraph_distributed_utils import serde
from langgraph_distributed_utils.conversion.config import (
    config_from_proto,
    config_to_proto,
    context_to_proto,
)
from langgraph_distributed_utils.conversion.orchestrator_response import (
    decode_response,
    decode_state_history_response,
    decode_state_response,
)
from langgraph_distributed_utils.conversion.runopts import runopts_to_proto
from langgraph_distributed_utils.conversion.value import value_to_proto
from langgraph_distributed_utils.proto import runtime_pb2, types_pb2
from langgraph_distributed_utils.proto.runtime_pb2 import OutputChunk
from langgraph_distributed_utils.proto.runtime_pb2_grpc import LangGraphRuntimeStub

var_child_runnable_config: ContextVar[RunnableConfig | None] = ContextVar(
    "child_runnable_config", default=None
)


def patch_pregel(runtime_client: LangGraphRuntimeStub, logger: logging.Logger):
    async def patched_ainvoke(
        pregel_self: Pregel,
        input: InputT | Command | None,
        config: RunnableConfig | None = None,
        **kwargs,
    ) -> dict[str | Any] | Any:
        return await _ainvoke_wrapper(
            runtime_client, logger, pregel_self, input, config, **kwargs
        )

    def patched_invoke(
        pregel_self: Pregel,
        input: InputT | Command | None,
        config: RunnableConfig | None = None,
        **kwargs,
    ) -> dict[str | Any] | Any:
        return _invoke_wrapper(
            runtime_client, logger, pregel_self, input, config, **kwargs
        )

    def patched_stream(
        pregel_self: Pregel,
        input: InputT | Command | None,
        config: RunnableConfig | None = None,
        **kwargs,
    ) -> Iterator[dict[str | Any] | Any]:
        return _stream_wrapper(
            runtime_client, logger, pregel_self, input, config, **kwargs
        )

    def patched_get_state_history(
        pregel_self,
        config: RunnableConfig | None = None,
        **kwargs,
    ) -> Iterator[StateSnapshot]:
        return _get_state_history_wrapper(runtime_client, pregel_self, config, **kwargs)

    def patched_get_state(
        pregel_self,
        config: RunnableConfig | None = None,
        **kwargs,
    ) -> StateSnapshot:
        return _get_state_wrapper(runtime_client, pregel_self, config, **kwargs)

    def patched_update_state(
        pregel_self,
        config: RunnableConfig,
        values: dict[str, Any] | Any | None,
        as_node: str | None = None,
        task_id: str | None = None,
    ) -> RunnableConfig:
        return _update_state_wrapper(
            runtime_client, pregel_self, config, values, as_node, task_id
        )

    def patched_bulk_update_state(
        pregel_self,
        config: RunnableConfig,
        supersteps: Sequence[Sequence[StateUpdate]],
    ) -> RunnableConfig:
        return _bulk_update_state_wrapper(
            runtime_client, pregel_self, config, supersteps
        )

    Pregel.ainvoke = patched_ainvoke  # type: ignore[invalid-assignment]
    Pregel.invoke = patched_invoke  # type: ignore[invalid-assignment]
    Pregel.stream = patched_stream  # type: ignore[invalid-assignment]
    Pregel.get_state_history = patched_get_state_history  # type: ignore[assignment]
    Pregel.get_state = patched_get_state  # type: ignore[assignment]
    Pregel.update_state = patched_update_state  # type: ignore[assignment]
    Pregel.bulk_update_state = patched_bulk_update_state  # type: ignore[assignment]


async def _ainvoke_wrapper(
    runtime_client: LangGraphRuntimeStub,
    logger: logging.Logger,
    pregel_self: Pregel,  # This is the actual Pregel instance
    input: InputT | Command | None,
    config: RunnableConfig | None = None,
    *,
    context: ContextT | None = None,
    stream_mode: StreamMode = "values",
    print_mode: StreamMode | Sequence[StreamMode] = (),
    output_keys: str | Sequence[str] | None = None,
    interrupt_before: All | Sequence[str] | None = None,
    interrupt_after: All | Sequence[str] | None = None,
    durability: Durability | None = None,
    subgraphs: bool | None = None,
    debug: bool | None = None,
    **kwargs: Any,
) -> dict[str, Any] | Any:
    """Wrapper that handles the actual invoke logic."""
    graph_name = pregel_self.name
    logger.info(f"pregel.ainvoke called on graph {graph_name}")

    # TODO: Hacky way of retrieving runtime from runnable context
    if not context:
        try:
            runtime = get_runtime()
            if runtime.context:
                context = runtime.context
        except Exception as e:
            logger.error(f"failed to retrive parent runtime for subgraph: {e}")

    if parent_config := var_child_runnable_config.get({}):
        config = ensure_config(config, parent_config)

    # create request
    invoke_request = runtime_pb2.InvokeRequest(
        graph_name=graph_name,
        input=value_to_proto(None, input),
        config=config_to_proto(config),
        context=context_to_proto(context),
        run_opts=runopts_to_proto(
            stream_mode,
            output_keys,
            interrupt_before,
            interrupt_after,
            durability,
            debug,
            subgraphs,
        ),
    )

    try:
        loop = asyncio.get_event_loop()
        response: runtime_pb2.OutputChunk = await loop.run_in_executor(
            None, runtime_client.Invoke, invoke_request
        )

        if response.WhichOneof("message") == "error":
            error_wrapper_value: types_pb2.Value = response.error
            raise parse_structured_error(error_wrapper_value.error)

    except grpc.RpcError as e:
        raise parse_error(e)

    # decode response
    return decode_response(response, stream_mode)


def _invoke_wrapper(
    runtime_client: LangGraphRuntimeStub,
    logger: logging.Logger,
    pregel_self: Pregel,
    input: InputT | Command | None,
    config: RunnableConfig | None = None,
    *,
    context: ContextT | None = None,
    stream_mode: StreamMode = "values",
    print_mode: StreamMode | Sequence[StreamMode] = (),
    output_keys: str | Sequence[str] | None = None,
    interrupt_before: All | Sequence[str] | None = None,
    interrupt_after: All | Sequence[str] | None = None,
    durability: Durability | None = None,
    subgraphs: bool | None = None,
    debug: bool | None = None,
    **kwargs: Any,
) -> dict[str, Any] | Any:
    """Wrapper that handles the actual invoke logic."""
    graph_name = pregel_self.name
    logger.info(f"pregel.invoke called on graph {graph_name}")

    # TODO: Hacky way of retrieving runtime from runnable context
    if not context:
        try:
            runtime = get_runtime()
            if runtime.context:
                context = runtime.context
        except Exception as e:
            logger.error(f"failed to retrive parent runtime for subgraph: {e}")

    # need to get config of parent because wont be available in orchestrator
    if parent_config := var_child_runnable_config.get({}):
        config = ensure_config(config, parent_config)

    # create request
    invoke_request = runtime_pb2.InvokeRequest(
        graph_name=graph_name,
        input=value_to_proto(None, input),
        config=config_to_proto(config),
        context=context_to_proto(context),
        run_opts=runopts_to_proto(
            stream_mode,
            output_keys,
            interrupt_before,
            interrupt_after,
            durability,
            debug,
            subgraphs,
        ),
    )

    try:
        response: OutputChunk = runtime_client.Invoke(invoke_request)
        if response.WhichOneof("message") == "error":
            error_wrapper_value: types_pb2.Value = response.error
            raise parse_structured_error(error_wrapper_value.error)

    except grpc.RpcError as e:
        # Unified error parsing: prefer JSON envelope; fallback heuristics inside parser.
        raise parse_error(e)

    # decode response
    return decode_response(response, stream_mode)


def _stream_wrapper(
    runtime_client: LangGraphRuntimeStub,
    logger: logging.Logger,
    pregel_self: Pregel,
    input: InputT | Command | None,
    config: RunnableConfig | None = None,
    *,
    context: ContextT | None = None,
    stream_mode: StreamMode | Sequence[StreamMode] | None = None,
    print_mode: StreamMode | Sequence[StreamMode] = (),
    output_keys: str | Sequence[str] | None = None,
    interrupt_before: All | Sequence[str] | None = None,
    interrupt_after: All | Sequence[str] | None = None,
    durability: Durability | None = None,
    subgraphs: bool | None = None,
    debug: bool | None = None,
    **kwargs: Any,
) -> Iterator[dict[str, Any] | Any]:
    graph_name = pregel_self.name
    logger.info(f"pregel.stream called on graph {graph_name}")

    # TODO: Hacky way of retrieving runtime from runnable context
    if not context:
        try:
            runtime = get_runtime()
            if runtime.context:
                context = runtime.context
        except Exception as e:
            logger.error(f"failed to retrive parent runtime for subgraph: {e}")

    # need to get config of parent because wont be available in orchestrator
    if parent_config := var_child_runnable_config.get({}):
        config = ensure_config(config, parent_config)

    # create request
    stream_request = runtime_pb2.StreamRequest(
        graph_name=graph_name,
        input=value_to_proto(None, input),
        config=config_to_proto(config),
        context=context_to_proto(context),
        run_opts=runopts_to_proto(
            stream_mode,
            output_keys,
            interrupt_before,
            interrupt_after,
            durability,
            debug,
            subgraphs,
        ),
    )

    try:
        response_stream = runtime_client.Stream(stream_request)
    except grpc.RpcError as e:
        # Unified error parsing: prefer JSON envelope; fallback heuristics inside parser.
        raise parse_error(e)

    for chunk in response_stream:
        yield decode_response(chunk, stream_mode)


def _get_state_history_wrapper(
    runtime_client: LangGraphRuntimeStub,
    pregel_self: Pregel,  # This is the actual Pregel instance
    config: RunnableConfig | None = None,
    *,
    filter: dict[str, Any] | None = None,
    before: RunnableConfig | None = None,
    limit: int | None = None,
) -> Iterator[StateSnapshot]:
    graph_name = pregel_self.name

    # create request
    filter_struct = Struct()  # type: ignore[unresolved-attribute]
    if filter is not None:
        filter_struct.update(filter)

    get_state_history_request = runtime_pb2.GetStateHistoryRequest(
        graph_name=graph_name,
        config=config_to_proto(config) if config else None,
        filter=filter_struct if filter else None,
        before=config_to_proto(before) if before else None,
        limit=limit,
    )

    # get and decode response
    # TODO We should make into true stream rpc instead of iterating over list
    try:
        response: runtime_pb2.GetStateHistoryResponse = runtime_client.GetStateHistory(
            get_state_history_request
        )
    except grpc.RpcError as e:
        raise parse_error(e)

    states = decode_state_history_response(response)

    yield from states


def _get_state_wrapper(
    runtime_client: LangGraphRuntimeStub,
    pregel_self: Pregel,
    config: RunnableConfig | None = None,
    *,
    subgraphs: bool = False,
) -> StateSnapshot:
    graph_name = pregel_self.name

    # create request
    get_state_request = runtime_pb2.GetStateRequest(
        graph_name=graph_name,
        config=config_to_proto(config) if config else None,
        subgraphs=subgraphs,
    )

    # get and decode response
    try:
        response: runtime_pb2.GetStateResponse = runtime_client.GetState(
            get_state_request
        )
    except grpc.RpcError as e:
        raise parse_error(e)

    return decode_state_response(response)


def _update_state_wrapper(
    runtime_client: LangGraphRuntimeStub,
    pregel_self: Pregel,
    config: RunnableConfig,
    values: dict[str, Any] | Any | None,
    as_node: str | None = None,
    task_id: str | None = None,
) -> RunnableConfig:
    graph_name = pregel_self.name
    # create request
    request = runtime_pb2.UpdateStateRequest(
        graph_name=graph_name,
        config=config_to_proto(config) if config else None,
        update=types_pb2.StateUpdate(
            values=value_to_proto(None, values), as_node=as_node, task_id=task_id
        ),
    )

    # get response
    try:
        response: runtime_pb2.UpdateStateResponse = runtime_client.UpdateState(request)
    except grpc.RpcError as e:
        raise parse_error(e)

    # decode response
    return config_from_proto(response.next_config)


def _bulk_update_state_wrapper(
    runtime_client: LangGraphRuntimeStub,
    pregel_self: Pregel,
    config: RunnableConfig,
    supersteps: Sequence[Sequence[StateUpdate]],
) -> RunnableConfig:
    graph_name = pregel_self.name

    # convert supersteps to proto
    supersteps_pb: Sequence[types_pb2.SuperstepUpdates] = []
    for superstep in supersteps:
        updates_pb: Sequence[StateUpdate] = []
        for update in superstep:
            update_pb = types_pb2.StateUpdate(
                values=value_to_proto(None, update.values),
                as_node=update.as_node,
                task_id=update.task_id,
            )

            updates_pb.append(update_pb)

        superstep_updates_pb = types_pb2.SuperstepUpdates(updates=updates_pb)
        supersteps_pb.append(superstep_updates_pb)

    # create request
    request = runtime_pb2.BulkUpdateStateRequest(
        graph_name=graph_name,
        config=config_to_proto(config) if config else None,
        supersteps=supersteps_pb,
    )

    # get response
    try:
        response: runtime_pb2.BulkUpdateStateResponse = runtime_client.BulkUpdateState(
            request
        )
    except grpc.RpcError as e:
        raise parse_error(e)

    # decode response
    return config_from_proto(response.next_config)


_ERROR_MAP = {
    # Canonical codes
    "GRAPH_RECURSION": GraphRecursionError,
    "GRAPH_BUBBLE_UP": GraphBubbleUp,
    "GRAPH_INTERRUPT": GraphInterrupt,
    "EMPTY_INPUT": EmptyInputError,
    "VALUE_ERROR": ValueError,
    "REMOTE_ERROR": Exception,
    "EXECUTOR_ERROR": Exception,
    "INVALID_UPDATE": ValueError,
    "EXECUTE_TASK": Exception,
    "RUNTIME_ERROR": RuntimeError,
    # Backward/compat names
    "GraphRecursionError": GraphRecursionError,
    "GraphBubbleUp": GraphBubbleUp,
    "GraphInterrupt": GraphInterrupt,
    "ParentCommand": ParentCommand,
    "ValueError": ValueError,
    "EmptyInputError": EmptyInputError,
}


def parse_structured_error(e: types_pb2.ExecutorError) -> Exception:
    # Try to parse interrupt
    if e.WhichOneof("error_type") == "graph_interrupt":
        graph_interrupt = e.graph_interrupt

        interrupts = []
        for interrupt in graph_interrupt.interrupts:
            interrupts.append(
                Interrupt(
                    value=serde.get_serializer().loads_typed(
                        (
                            interrupt.value.base_value.method,
                            interrupt.value.base_value.value,
                        )
                    ),
                    id=interrupt.id,
                )
            )
        raise GraphInterrupt(interrupts)
    else:
        raise ValueError(f"Unknown subgraph error from orchestrator: {e!s}")


def parse_error(e: grpc.RpcError) -> Exception:
    if (
        (details := getattr(e, "details", None))
        and callable(details)
        and (det := details())
        and isinstance(det, str)
    ):
        return parse_error_detail(det)
    return e


def parse_error_detail(detail: str) -> Exception:
    # First try JSON envelope
    try:
        details = orjson.loads(detail)
        code = details.get("code") or details.get("error")
        exc_type = _ERROR_MAP.get(code) or Exception
        message = details.get("message") or ""
        return exc_type(message)
    except orjson.JSONDecodeError:
        pass

    # Fallback: legacy heuristics for certain server-side validation errors
    lowered = detail.lower()
    if "recursion limit exceeded" in lowered:
        return GraphRecursionError()
    if "invalid context format" in lowered:
        return TypeError("invalid context format")
    if "invalid pydantic context format" in lowered:
        # Attempt to extract trailing JSON error data if present: ": { ... }"
        try:
            import json as _json

            if ": {" in detail:
                json_part = "{" + detail.split(": {", 1)[1]
                error_data = _json.loads(json_part)
                return ValidationError.from_exception_data(
                    error_data.get("title", "ValidationError"),
                    error_data.get("errors", []),
                )
        except Exception:
            # fall through to generic Exception
            pass
    return Exception(detail)


__all__ = [
    "parse_error",
    "patch_pregel",
]
