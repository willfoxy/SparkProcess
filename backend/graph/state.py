"""
Double Diamond LangGraph State definition.

The state flows through four phases and two security checkpoints:

  START
    └─ Phase 1: Explorer (parallel × 6)
    └─ Phase 2: Definer (sequential × 5)
    └─ Security Checkpoint 1
    └─ Phase 3: Creator (parallel × 5)
    └─ Phase 4: Launch & Ops (sequential × 5)
    └─ Security Checkpoint 2
  END

All agent outputs are stored here.  The `Annotated` type hints use
custom reducers so parallel agents can safely write to the same key.
"""

from __future__ import annotations

import operator
from typing import Annotated, Any

from typing_extensions import TypedDict


def _merge_dicts(a: dict, b: dict) -> dict:
    """Merge two dicts, newer values win on conflict."""
    return {**a, **b}


def _first_value(a: Any, b: Any) -> Any:
    """Keep the first non-None value (used for fields set once)."""
    return a if a is not None else b


# ---------------------------------------------------------------------------
# Main state schema
# ---------------------------------------------------------------------------

class DoubleDiamondState(TypedDict):
    # ---- Session metadata ------------------------------------------------
    session_id: str
    brief: str                           # The innovation challenge / brief
    organization: str                    # Organisation name (optional)
    created_at: str                      # ISO timestamp

    # ---- Phase tracking --------------------------------------------------
    current_phase: str                   # explorer | definer | creator | launch_ops | security | done
    phase_statuses: Annotated[dict, _merge_dicts]   # {phase: pending|running|done|failed}

    # ---- Phase 1: Explorer outputs (parallel, merged) --------------------
    explorer_outputs: Annotated[dict, _merge_dicts]

    # ---- Phase 2: Definer outputs (sequential) ---------------------------
    definer_outputs: Annotated[dict, _merge_dicts]

    # ---- Security Checkpoint 1 ------------------------------------------
    security_check_1: Annotated[dict, _first_value]

    # ---- Phase 3: Creator outputs (parallel, merged) --------------------
    creator_outputs: Annotated[dict, _merge_dicts]

    # ---- Phase 4: Launch & Ops outputs (sequential) ---------------------
    launch_ops_outputs: Annotated[dict, _merge_dicts]

    # ---- Security Checkpoint 2 ------------------------------------------
    security_check_2: Annotated[dict, _first_value]

    # ---- Event log (SSE stream) ------------------------------------------
    events: Annotated[list[dict], operator.add]

    # ---- Errors ----------------------------------------------------------
    errors: Annotated[list[str], operator.add]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_event(
    event_type: str,
    phase: str,
    agent: str | None = None,
    status: str = "running",
    message: str = "",
    data: dict | None = None,
) -> dict:
    """Build a standardised event dict for the SSE stream."""
    import datetime
    return {
        "type": event_type,        # phase_start | agent_start | agent_done | security_check | error
        "phase": phase,
        "agent": agent,
        "status": status,          # running | done | flagged | rejected | error
        "message": message,
        "data": data or {},
        "timestamp": datetime.datetime.utcnow().isoformat(),
    }


def initial_state(session_id: str, brief: str, organization: str = "") -> DoubleDiamondState:
    """Create the initial state for a new pipeline run."""
    import datetime
    return DoubleDiamondState(
        session_id=session_id,
        brief=brief,
        organization=organization,
        created_at=datetime.datetime.utcnow().isoformat(),
        current_phase="explorer",
        phase_statuses={
            "explorer": "pending",
            "definer": "pending",
            "security_1": "pending",
            "creator": "pending",
            "launch_ops": "pending",
            "security_2": "pending",
        },
        explorer_outputs={},
        definer_outputs={},
        security_check_1={},
        creator_outputs={},
        launch_ops_outputs={},
        security_check_2={},
        events=[],
        errors=[],
    )
