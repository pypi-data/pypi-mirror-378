from collections.abc import AsyncIterator, Iterator
from uuid import UUID

from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.messages import BaseMessage
from langchain_core.outputs import ChatGeneration, ChatGenerationChunk, LLMResult

try:
    from langchain_core.tracers._streaming import _StreamingCallbackHandler
except ImportError:
    _StreamingCallbackHandler = object  # type: ignore

import logging
from typing import Any, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")
Meta = tuple[tuple[str, ...], dict[str, Any]]
NS_SEP = "|"


class ExecutorStreamHandler(BaseCallbackHandler, _StreamingCallbackHandler):
    """Callback handler that captures LLM streaming tokens for Go executor."""

    def __init__(self, stream_callback, task_id: str):
        """Initialize handler with callback to send stream chunks.

        Args:
            stream_callback: Function to call with stream chunks
            task_id: Task ID for metadata
        """
        self.stream_callback = stream_callback
        self.task_id = task_id
        self.metadata = {}  # Track run metadata like StreamMessagesHandler
        self.seen: set[int | str] = set()

    def on_llm_start(
        self,
        serialized: dict,
        prompts: list[str],
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        tags: list[str] | None = None,
        metadata: dict | None = None,
        **kwargs,
    ) -> None:
        """Store metadata for this LLM run."""
        if metadata:
            # Store minimal metadata needed for streaming context
            self.metadata[run_id] = {"task_id": self.task_id, "metadata": metadata}

    def on_llm_new_token(
        self,
        token: str,
        *,
        chunk: ChatGenerationChunk | None = None,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        tags: list[str] | None = None,
        **kwargs,
    ) -> None:
        """Stream LLM token chunks immediately to Go."""
        if not isinstance(chunk, ChatGenerationChunk):
            return

        if run_id in self.metadata:
            self._emit(self.metadata[run_id], chunk.message, run_id=run_id)

    def on_llm_end(
        self,
        response: LLMResult,
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        **kwargs,
    ) -> None:
        """Handle final LLM result (will be handled by deduplication in Go)."""
        # Clean up metadata
        if metadata := self.metadata.pop(run_id, None):
            if response.generations and response.generations[0]:
                gen = response.generations[0][0]
                if isinstance(gen, ChatGeneration):
                    msg = gen.message
                    self._emit(metadata, msg, run_id=run_id, dedupe=True)
                    if msg_id := msg.id:
                        self.seen.discard(msg_id)

    def on_llm_error(
        self,
        error: BaseException,
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        **kwargs,
    ) -> None:
        """Clean up on LLM error."""
        self.metadata.pop(run_id, None)

    def tap_output_aiter(
        self, run_id: UUID, output: AsyncIterator[T]
    ) -> AsyncIterator[T]:
        return output

    def tap_output_iter(self, run_id: UUID, output: Iterator[T]) -> Iterator[T]:
        return output

    def _emit(
        self,
        meta: dict[str, Any],
        message: BaseMessage,
        *,
        dedupe: bool = False,
        run_id: UUID,
    ) -> None:
        if dedupe and message.id in self.seen:
            logger.debug("deduped", extra={"run_id": run_id, "message_id": message.id})
            return
        else:
            if message.id is None:
                message.id = f"run--{run_id}"
            self.seen.add(message.id)
            self.stream_callback(message, meta)
