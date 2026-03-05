"""
FastAPI application — Double Diamond AI Orchestration API.

Endpoints:
  POST /api/sessions              — Create and start a new pipeline session
  GET  /api/sessions              — List all sessions (from memory store)
  GET  /api/sessions/{id}         — Get session state + all outputs
  GET  /api/sessions/{id}/stream  — SSE stream of live pipeline events
  DELETE /api/sessions/{id}       — Clear session memory

The pipeline runs as a background task.  The SSE endpoint polls the
event queue and pushes events to connected clients.
"""

from __future__ import annotations

import asyncio
import json
import uuid
from asyncio import Queue
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import AsyncGenerator

import structlog
from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from backend.config import get_settings
from backend.graph.pipeline import get_pipeline
from backend.graph.state import DoubleDiamondState, initial_state, make_event
from backend.memory.aws_memory import memory_store
from backend.observability.datadog import init_datadog, workflow_span

logger = structlog.get_logger(__name__)
settings = get_settings()

# ---------------------------------------------------------------------------
# In-memory event queues (session_id → list of subscriber queues)
# ---------------------------------------------------------------------------

_event_queues: dict[str, list[Queue]] = {}
_session_states: dict[str, DoubleDiamondState] = {}


# ---------------------------------------------------------------------------
# Lifespan
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting SparkProcess API")
    init_datadog(
        api_key=settings.dd_api_key,
        site=settings.dd_site,
        service=settings.dd_service,
        env=settings.dd_env,
        ml_app=settings.dd_ml_app,
        enabled=settings.dd_llm_obs_enabled,
    )
    yield
    logger.info("Shutting down SparkProcess API")


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = FastAPI(
    title="SparkProcess — Double Diamond AI Orchestration",
    description="Autonomous AI innovation process powered by LangGraph + AWS Bedrock",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------

class CreateSessionRequest(BaseModel):
    brief: str = Field(..., min_length=20, description="The innovation challenge or brief")
    organization: str = Field(default="", description="Organisation name")


class SessionSummary(BaseModel):
    session_id: str
    brief: str
    organization: str
    created_at: str
    current_phase: str
    phase_statuses: dict
    security_check_1: dict
    security_check_2: dict


class SessionDetail(SessionSummary):
    explorer_outputs: dict
    definer_outputs: dict
    creator_outputs: dict
    launch_ops_outputs: dict
    events: list[dict]
    errors: list[str]


# ---------------------------------------------------------------------------
# Background pipeline runner
# ---------------------------------------------------------------------------

def _push_event(session_id: str, event: dict) -> None:
    """Push an event to all SSE subscribers for this session."""
    for q in _event_queues.get(session_id, []):
        try:
            q.put_nowait(event)
        except asyncio.QueueFull:
            pass


async def _run_pipeline(session_id: str, state: DoubleDiamondState) -> None:
    """Execute the Double Diamond pipeline and broadcast events via SSE."""
    pipeline = get_pipeline()

    # Announce start
    _push_event(session_id, make_event("pipeline_start", phase="explorer",
                                       status="running", message="Pipeline starting…"))

    try:
        with workflow_span(name="double_diamond", session_id=session_id, phase="full"):
            async for chunk in pipeline.astream(state, stream_mode="updates"):
                # chunk is {node_name: partial_state_update}
                for node_name, update in chunk.items():
                    _session_states[session_id] = {
                        **_session_states.get(session_id, {}),
                        **update,
                    }
                    # Broadcast any new events from this update
                    for event in update.get("events", []):
                        _push_event(session_id, event)

    except Exception as exc:
        logger.error("Pipeline failed", session_id=session_id, error=str(exc))
        err_event = make_event("error", phase="unknown", status="error", message=str(exc))
        _push_event(session_id, err_event)
        _session_states[session_id] = {
            **_session_states.get(session_id, {}),
            "errors": [str(exc)],
            "current_phase": "done",
        }
    finally:
        # Signal stream end
        _push_event(session_id, {"type": "stream_end", "session_id": session_id})
        # Remove finished queues
        _event_queues.pop(session_id, None)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.post("/api/sessions", response_model=SessionSummary, status_code=201)
async def create_session(
    body: CreateSessionRequest,
    background_tasks: BackgroundTasks,
) -> SessionSummary:
    """Create a new pipeline session and start the Double Diamond process."""
    session_id = str(uuid.uuid4())
    state = initial_state(
        session_id=session_id,
        brief=body.brief,
        organization=body.organization,
    )
    _session_states[session_id] = state
    _event_queues[session_id] = []

    # Persist initial state
    memory_store.save(session_id, "initial_state", {
        "brief": body.brief,
        "organization": body.organization,
        "created_at": state["created_at"],
    })

    # Run pipeline in background
    background_tasks.add_task(_run_pipeline, session_id, state)

    logger.info("Session created", session_id=session_id)
    return SessionSummary(
        session_id=session_id,
        brief=body.brief,
        organization=body.organization,
        created_at=state["created_at"],
        current_phase=state["current_phase"],
        phase_statuses=state["phase_statuses"],
        security_check_1={},
        security_check_2={},
    )


@app.get("/api/sessions", response_model=list[SessionSummary])
async def list_sessions() -> list[SessionSummary]:
    """List all in-memory sessions."""
    result = []
    for sid, s in _session_states.items():
        result.append(SessionSummary(
            session_id=sid,
            brief=s.get("brief", ""),
            organization=s.get("organization", ""),
            created_at=s.get("created_at", ""),
            current_phase=s.get("current_phase", ""),
            phase_statuses=s.get("phase_statuses", {}),
            security_check_1=s.get("security_check_1", {}),
            security_check_2=s.get("security_check_2", {}),
        ))
    return result


@app.get("/api/sessions/{session_id}", response_model=SessionDetail)
async def get_session(session_id: str) -> SessionDetail:
    """Get full session state including all agent outputs."""
    s = _session_states.get(session_id)
    if not s:
        # Try loading from memory store
        stored = memory_store.load_session(session_id)
        if not stored:
            raise HTTPException(status_code=404, detail="Session not found")
        s = stored

    return SessionDetail(
        session_id=session_id,
        brief=s.get("brief", ""),
        organization=s.get("organization", ""),
        created_at=s.get("created_at", ""),
        current_phase=s.get("current_phase", ""),
        phase_statuses=s.get("phase_statuses", {}),
        security_check_1=s.get("security_check_1", {}),
        security_check_2=s.get("security_check_2", {}),
        explorer_outputs=s.get("explorer_outputs", {}),
        definer_outputs=s.get("definer_outputs", {}),
        creator_outputs=s.get("creator_outputs", {}),
        launch_ops_outputs=s.get("launch_ops_outputs", {}),
        events=s.get("events", []),
        errors=s.get("errors", []),
    )


@app.delete("/api/sessions/{session_id}", status_code=204)
async def delete_session(session_id: str) -> None:
    """Remove a session from memory."""
    _session_states.pop(session_id, None)
    _event_queues.pop(session_id, None)
    memory_store.clear_session(session_id)


# ---------------------------------------------------------------------------
# SSE Stream
# ---------------------------------------------------------------------------

@app.get("/api/sessions/{session_id}/stream")
async def stream_session(session_id: str) -> StreamingResponse:
    """
    Server-Sent Events stream for real-time pipeline updates.

    Each event is a JSON-encoded dict with the shape:
    {
      "type": "agent_done" | "phase_start" | "security_check" | "error" | "stream_end",
      "phase": "explorer" | "definer" | ...,
      "agent": "market_insights" | null,
      "status": "running" | "done" | "approved" | "flagged" | "rejected" | "error",
      "message": "...",
      "data": {...},
      "timestamp": "ISO8601"
    }
    """
    if session_id not in _session_states:
        raise HTTPException(status_code=404, detail="Session not found")

    # Create a queue for this subscriber
    q: Queue = Queue(maxsize=500)
    _event_queues.setdefault(session_id, []).append(q)

    async def event_generator() -> AsyncGenerator[str, None]:
        # Send current state snapshot first
        state = _session_states.get(session_id, {})
        snapshot = make_event(
            "snapshot", phase=state.get("current_phase", "explorer"),
            status="running", message="Connected",
            data={"phase_statuses": state.get("phase_statuses", {})},
        )
        yield f"data: {json.dumps(snapshot)}\n\n"

        try:
            while True:
                try:
                    event = await asyncio.wait_for(q.get(), timeout=30.0)
                    yield f"data: {json.dumps(event)}\n\n"
                    if event.get("type") == "stream_end":
                        break
                except asyncio.TimeoutError:
                    # Heartbeat to keep connection alive
                    yield "data: {\"type\": \"heartbeat\"}\n\n"
        finally:
            # Clean up subscriber
            queues = _event_queues.get(session_id, [])
            if q in queues:
                queues.remove(q)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "spark-process",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "active_sessions": len(_session_states),
    }
