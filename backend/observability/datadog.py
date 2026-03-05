"""
Datadog LLM Observability integration.

Wraps every LLM call with LLMObs spans so you get:
- Full input/output tracing
- Token usage
- Latency per agent
- Error tracking
- Model metadata
"""

import functools
import logging
from contextlib import contextmanager
from typing import Any, Generator

import structlog

logger = structlog.get_logger(__name__)


def _try_import_ddtrace():
    try:
        from ddtrace.llmobs import LLMObs
        from ddtrace import tracer
        return LLMObs, tracer
    except ImportError:
        logger.warning("ddtrace not available — LLM observability disabled")
        return None, None


LLMObs, _tracer = _try_import_ddtrace()
_initialized = False


def init_datadog(
    *,
    api_key: str,
    site: str,
    service: str,
    env: str,
    ml_app: str,
    enabled: bool = True,
) -> None:
    """Initialise Datadog LLM Observability. Call once at startup."""
    global _initialized

    if not enabled or not LLMObs:
        logger.info("Datadog LLM Observability disabled or ddtrace not installed")
        return

    if _initialized:
        return

    import os
    os.environ.setdefault("DD_API_KEY", api_key)
    os.environ.setdefault("DD_SITE", site)
    os.environ.setdefault("DD_ENV", env)
    os.environ.setdefault("DD_SERVICE", service)
    os.environ.setdefault("DD_LLMOBS_ML_APP", ml_app)

    LLMObs.enable(
        ml_app=ml_app,
        integrations_enabled=False,  # We wrap manually for full control
    )
    _initialized = True
    logger.info("Datadog LLM Observability initialised", ml_app=ml_app, env=env)


@contextmanager
def llm_span(
    *,
    name: str,
    model_provider: str = "anthropic",
    model_name: str,
    agent_role: str,
    session_id: str,
    phase: str,
    messages: list[dict],
) -> Generator[Any, None, None]:
    """
    Context manager that wraps an LLM call with a Datadog LLMObs span.

    Usage:
        with llm_span(name="market_insights_call", model_name="...", ...) as span:
            response = bedrock_client.messages.create(...)
            annotate_llm_output(span, response)
    """
    if not LLMObs or not _initialized:
        yield None
        return

    with LLMObs.llm(
        model_provider=model_provider,
        model_name=model_name,
        name=name,
        session_id=session_id,
    ) as span:
        if span:
            LLMObs.annotate(
                span=span,
                input_data=messages,
                tags={
                    "agent_role": agent_role,
                    "phase": phase,
                    "session_id": session_id,
                },
            )
        yield span


def annotate_llm_output(span: Any, response_text: str, usage: dict | None = None) -> None:
    """Annotate a span with the LLM output after the call completes."""
    if not LLMObs or not span:
        return

    annotation_kwargs: dict = {"output_data": response_text}
    if usage:
        annotation_kwargs["metrics"] = {
            "input_tokens": usage.get("input_tokens", 0),
            "output_tokens": usage.get("output_tokens", 0),
        }

    LLMObs.annotate(span=span, **annotation_kwargs)


@contextmanager
def workflow_span(*, name: str, session_id: str, phase: str) -> Generator[Any, None, None]:
    """Wrap a multi-step workflow (e.g., an entire phase) with an LLMObs workflow span."""
    if not LLMObs or not _initialized:
        yield None
        return

    with LLMObs.workflow(name=name, session_id=session_id) as span:
        if span:
            LLMObs.annotate(span=span, tags={"phase": phase, "session_id": session_id})
        yield span


@contextmanager
def agent_span(*, name: str, session_id: str) -> Generator[Any, None, None]:
    """Wrap a full autonomous agent cycle with an LLMObs agent span."""
    if not LLMObs or not _initialized:
        yield None
        return

    with LLMObs.agent(name=name, session_id=session_id) as span:
        yield span


def record_error(span: Any, error: Exception) -> None:
    """Record an error on the active span."""
    if not span:
        return
    try:
        span.set_tag("error", True)
        span.set_tag("error.message", str(error))
        span.set_tag("error.type", type(error).__name__)
    except Exception:
        pass
