import logging
from collections.abc import Iterable, Sequence

import grpc
import grpc.aio
import orjson
from langgraph.store.base import BaseStore, GetOp, Item, Op, PutOp, Result
from langgraph_distributed_utils.proto import runtime_pb2, runtime_pb2_grpc

LOGGER = logging.getLogger(__name__)


class RemoteStore(BaseStore):
    def __init__(self, sync_channel: grpc.Channel, async_channel: grpc.aio.Channel):
        """
        Dual-channel RemoteStore implementation:
        - sync_channel: Used for batch() method (sync operations)
        - async_channel: Used for abatch() method (async operations)
        """
        self._sync_client = runtime_pb2_grpc.LangGraphRuntimeStub(sync_channel)
        self._async_client = runtime_pb2_grpc.LangGraphRuntimeStub(async_channel)

    async def abatch(self, ops: Iterable[Op]) -> list[Result]:
        """Async batch operations using true async gRPC client"""
        proto_ops = [self._convert_op_to_proto(op) for op in ops]
        request = runtime_pb2.BatchStoreOperationRequest(ops=proto_ops)

        try:
            response = await self._async_client.BatchStoreOperation(request)

            return self._convert_proto_results_to_langgraph(response.ops, proto_ops)

        except grpc.RpcError as e:
            LOGGER.error(f"gRPC error in abatch: {e}")
            raise RuntimeError(f"Store operation failed: {e}")

    def batch(self, ops: Iterable[Op]) -> list[Result]:
        """Sync batch operations using sync gRPC client"""
        proto_ops = [self._convert_op_to_proto(op) for op in ops]
        request = runtime_pb2.BatchStoreOperationRequest(ops=proto_ops)

        try:
            response = self._sync_client.BatchStoreOperation(request)
            return self._convert_proto_results_to_langgraph(response.ops, proto_ops)

        except grpc.RpcError as e:
            LOGGER.error(f"gRPC error in batch: {e}")
            raise RuntimeError(f"Store operation failed: {e}")

    def _convert_op_to_proto(self, op: Op) -> runtime_pb2.SingleStoreOperation:
        if isinstance(op, GetOp):
            get_op = runtime_pb2.GetItemOperation(
                prefix=op.namespace, key=op.key, refreshTTL=op.refresh_ttl
            )
            return runtime_pb2.SingleStoreOperation(
                OperationType=runtime_pb2.StoreOperationEntryType.GET, get=get_op
            )

        elif isinstance(op, PutOp):
            # Convert value to JSON string
            json_value = (
                orjson.dumps(op.value).decode("utf-8") if op.value is not None else ""
            )

            # Handle TTL: protobuf doesn't accept None, use 0 as default
            ttl_minutes = 0
            if op.ttl is not None and isinstance(op.ttl, float):
                ttl_minutes = int(op.ttl)

            put_op = runtime_pb2.PutItemOperation(
                prefix=op.namespace,
                key=op.key,
                jsonValue=json_value,
                ttlMinutes=ttl_minutes,
            )
            return runtime_pb2.SingleStoreOperation(
                OperationType=runtime_pb2.StoreOperationEntryType.PUT, put=put_op
            )
        else:
            LOGGER.warning(f"Unsupported operation type: {type(op)}")
            raise NotImplementedError(f"Unsupported operation type: {type(op)}")

    def _convert_proto_results_to_langgraph(
        self,
        proto_results: Sequence[runtime_pb2.SingleStoreOperationResult],
        proto_ops: Sequence[runtime_pb2.SingleStoreOperation],
    ) -> list[Result]:
        """Convert protobuf results back to LangGraph Results"""
        results = []

        for proto_result, proto_op in zip(proto_results, proto_ops, strict=True):
            if proto_result.OperationType == runtime_pb2.StoreOperationEntryType.GET:
                # Parse JSON value back to dict
                try:
                    value = (
                        orjson.loads(proto_result.get.jsonValue)
                        if proto_result.get.jsonValue
                        else None
                    )

                    # Create Item result
                    item = Item(
                        namespace=proto_op.get.prefix,
                        key=proto_op.get.key,
                        value=value,
                        created_at=proto_result.get.createdAt.ToDatetime(),
                        updated_at=proto_result.get.updatedAt.ToDatetime(),
                    )
                    results.append(item)
                except orjson.JSONDecodeError as e:
                    LOGGER.error(f"Failed to decode JSON value: {e}")
                    raise e
            elif proto_result.OperationType == runtime_pb2.StoreOperationEntryType.PUT:
                results.append(None)
            else:
                LOGGER.warning(
                    f"Unsupported operation type: {type(proto_result.OperationType)}"
                )
                raise ValueError(
                    f"Unsupported operation type: {type(proto_result.OperationType)}"
                )

        return results
