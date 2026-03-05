"""
Base agent class — wraps AWS Bedrock + Datadog LLM Observability.

Every specialist agent inherits from BaseAgent and calls
`self.invoke(messages)` or `self.stream(messages)` to interact with
the LLM.  All calls are automatically traced by Datadog.
"""

from __future__ import annotations

import asyncio
from typing import AsyncGenerator

import anthropic
import structlog

from backend.config import get_settings
from backend.observability.datadog import annotate_llm_output, llm_span, record_error

logger = structlog.get_logger(__name__)
settings = get_settings()


def _make_bedrock_client() -> anthropic.AnthropicBedrock:
    kwargs: dict = {"aws_region": settings.aws_region}
    if settings.aws_access_key_id:
        kwargs["aws_access_key_id"] = settings.aws_access_key_id
        kwargs["aws_secret_access_key"] = settings.aws_secret_access_key
        if settings.aws_session_token:
            kwargs["aws_session_token"] = settings.aws_session_token
    return anthropic.AnthropicBedrock(**kwargs)


# Shared Bedrock client — one per process
_bedrock_client: anthropic.AnthropicBedrock | None = None


def get_bedrock_client() -> anthropic.AnthropicBedrock:
    global _bedrock_client
    if _bedrock_client is None:
        _bedrock_client = _make_bedrock_client()
    return _bedrock_client


class BaseAgent:
    """
    Foundation for all Double Diamond agents.

    Subclasses must set:
        role       – short identifier, e.g. "market_insights"
        phase      – one of: explorer | definer | creator | launch_ops | security
        system     – the system prompt for this agent
    """

    role: str = "base"
    phase: str = "unknown"
    system: str = "You are a helpful AI assistant."
    model_id: str = settings.bedrock_model_id

    def __init__(self, session_id: str = "default"):
        self.session_id = session_id
        self._client = get_bedrock_client()

    # ------------------------------------------------------------------
    # Synchronous invoke
    # ------------------------------------------------------------------

    def invoke(self, messages: list[dict], **kwargs) -> str:
        """Call the LLM and return the full response text."""
        span_ctx = llm_span(
            name=f"{self.role}_call",
            model_name=self.model_id,
            agent_role=self.role,
            session_id=self.session_id,
            phase=self.phase,
            messages=messages,
        )

        with span_ctx as span:
            try:
                response = self._client.messages.create(
                    model=self.model_id,
                    max_tokens=kwargs.get("max_tokens", settings.max_tokens_per_agent),
                    system=self.system,
                    messages=messages,
                )
                text = response.content[0].text
                usage = {
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                }
                annotate_llm_output(span, text, usage)
                logger.info(
                    "Agent invoked",
                    role=self.role,
                    phase=self.phase,
                    input_tokens=usage["input_tokens"],
                    output_tokens=usage["output_tokens"],
                )
                return text
            except Exception as exc:
                record_error(span, exc)
                logger.error("Agent invocation failed", role=self.role, error=str(exc))
                raise

    # ------------------------------------------------------------------
    # Streaming invoke (async)
    # ------------------------------------------------------------------

    async def stream(self, messages: list[dict], **kwargs) -> AsyncGenerator[str, None]:
        """Stream the LLM response token by token."""
        loop = asyncio.get_event_loop()

        def _run_stream():
            chunks = []
            with self._client.messages.stream(
                model=self.model_id,
                max_tokens=kwargs.get("max_tokens", settings.max_tokens_per_agent),
                system=self.system,
                messages=messages,
            ) as stream:
                for text in stream.text_stream:
                    chunks.append(text)
                    yield text
            return "".join(chunks)

        # Wrap synchronous streaming for async callers
        for chunk in _run_stream():
            yield chunk
            await asyncio.sleep(0)  # yield control

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def build_prompt(self, brief: str, context: str = "") -> list[dict]:
        """Default prompt builder — override in subclasses for custom structure."""
        user_content = f"Brief / Challenge:\n{brief}"
        if context:
            user_content += f"\n\nAdditional Context:\n{context}"
        return [{"role": "user", "content": user_content}]
