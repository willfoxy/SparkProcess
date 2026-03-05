"""
Double Diamond LangGraph Pipeline.

Graph topology:
  START
    → explorer_fan_out          (conditional edge returns 6 × Send)
    → [market_insights_node, ethnographic_node, competitive_node,
       data_mining_node, trend_scouting_node, tech_spikes_node]  (parallel)
    → explorer_gather           (join all explorer outputs)
    → data_synthesiser_node
    → problem_definer_node
    → persona_developer_node
    → goal_setter_node
    → problem_framer_node
    → security_checkpoint_1     (APPROVED → creator_fan_out, REJECTED → END)
    → creator_fan_out           (conditional edge returns 5 × Send)
    → [ideation_node, prototyping_node, uiux_node, code_dev_node, ab_testing_node]  (parallel)
    → creator_gather            (join all creator outputs)
    → launch_orchestration_node
    → governance_node
    → monitoring_node
    → customer_support_node
    → continuous_updates_node
    → security_checkpoint_2     (APPROVED → END, REJECTED → END with flag)
  END
"""

from __future__ import annotations

from typing import Any

import structlog
from langgraph.graph import END, START, StateGraph
from langgraph.types import Send

from backend.agents.creator_agents import (
    ABTestingAgent,
    CodeDevelopmentAgent,
    IdeationAgent,
    PrototypingAgent,
    UIUXAgent,
)
from backend.agents.definer_agents import (
    DataSynthesiserAgent,
    GoalSetterAgent,
    PersonaDeveloperAgent,
    ProblemDefinerAgent,
    ProblemFramerAgent,
)
from backend.agents.explorer_agents import (
    CompetitiveAnalysisAgent,
    DataMiningAgent,
    EthnographicAgent,
    MarketInsightsAgent,
    TechSpikesAgent,
    TrendScoutingAgent,
)
from backend.agents.launch_ops_agents import (
    ContinuousUpdateAgent,
    CustomerSupportAgent,
    GovernanceAgent,
    LaunchOrchestrationAgent,
    MonitoringAgent,
)
from backend.agents.security_agent import SecurityAgent, SecurityDecision
from backend.config import get_settings
from backend.graph.state import DoubleDiamondState, make_event
from backend.memory.aws_memory import memory_store
from backend.observability.datadog import workflow_span

logger = structlog.get_logger(__name__)
settings = get_settings()


# ---------------------------------------------------------------------------
# Utility: build agent with correct session_id
# ---------------------------------------------------------------------------

def _agent(cls, state: DoubleDiamondState):
    return cls(session_id=state["session_id"])


# ===========================================================================
# PHASE 1 — Explorer Nodes (run in parallel via Send)
# ===========================================================================

def explorer_fan_out(state: DoubleDiamondState) -> list[Send]:
    """Fan out to all six explorer agents simultaneously."""
    return [
        Send("market_insights_node", state),
        Send("ethnographic_node", state),
        Send("competitive_node", state),
        Send("data_mining_node", state),
        Send("trend_scouting_node", state),
        Send("tech_spikes_node", state),
    ]


def _explorer_event(state, agent_role, status, output=""):
    return make_event("agent_done" if status == "done" else "agent_start",
                      phase="explorer", agent=agent_role, status=status, message=output[:200])


def market_insights_node(state: DoubleDiamondState) -> dict:
    result = _agent(MarketInsightsAgent, state).run(state["brief"])
    return {
        "explorer_outputs": {"market_insights": result},
        "events": [_explorer_event(state, "market_insights", "done", result["output"])],
    }


def ethnographic_node(state: DoubleDiamondState) -> dict:
    result = _agent(EthnographicAgent, state).run(state["brief"])
    return {
        "explorer_outputs": {"ethnographic_research": result},
        "events": [_explorer_event(state, "ethnographic_research", "done", result["output"])],
    }


def competitive_node(state: DoubleDiamondState) -> dict:
    result = _agent(CompetitiveAnalysisAgent, state).run(state["brief"])
    return {
        "explorer_outputs": {"competitive_analysis": result},
        "events": [_explorer_event(state, "competitive_analysis", "done", result["output"])],
    }


def data_mining_node(state: DoubleDiamondState) -> dict:
    result = _agent(DataMiningAgent, state).run(state["brief"])
    return {
        "explorer_outputs": {"data_mining": result},
        "events": [_explorer_event(state, "data_mining", "done", result["output"])],
    }


def trend_scouting_node(state: DoubleDiamondState) -> dict:
    result = _agent(TrendScoutingAgent, state).run(state["brief"])
    return {
        "explorer_outputs": {"trend_scouting": result},
        "events": [_explorer_event(state, "trend_scouting", "done", result["output"])],
    }


def tech_spikes_node(state: DoubleDiamondState) -> dict:
    result = _agent(TechSpikesAgent, state).run(state["brief"])
    return {
        "explorer_outputs": {"tech_spikes": result},
        "events": [_explorer_event(state, "tech_spikes", "done", result["output"])],
    }


def explorer_gather(state: DoubleDiamondState) -> dict:
    """Gather all explorer outputs and persist to memory."""
    memory_store.save_phase(state["session_id"], "explorer", state["explorer_outputs"])
    return {
        "current_phase": "definer",
        "phase_statuses": {"explorer": "done", "definer": "running"},
        "events": [make_event("phase_start", phase="definer", status="running",
                              message="All explorer agents complete. Starting definer phase.")],
    }


# ===========================================================================
# PHASE 2 — Definer Nodes (sequential)
# ===========================================================================

def data_synthesiser_node(state: DoubleDiamondState) -> dict:
    result = _agent(DataSynthesiserAgent, state).run(state["brief"], state["explorer_outputs"])
    return {
        "definer_outputs": {"data_synthesiser": result},
        "events": [make_event("agent_done", phase="definer", agent="data_synthesiser",
                              status="done", message=result["output"][:200])],
    }


def problem_definer_node(state: DoubleDiamondState) -> dict:
    synthesis = state["definer_outputs"].get("data_synthesiser", {}).get("output", "")
    result = _agent(ProblemDefinerAgent, state).run(state["brief"], synthesis)
    return {
        "definer_outputs": {"problem_definer": result},
        "events": [make_event("agent_done", phase="definer", agent="problem_definer",
                              status="done", message=result["output"][:200])],
    }


def persona_developer_node(state: DoubleDiamondState) -> dict:
    synthesis = state["definer_outputs"].get("data_synthesiser", {}).get("output", "")
    problems = state["definer_outputs"].get("problem_definer", {}).get("output", "")
    result = _agent(PersonaDeveloperAgent, state).run(state["brief"], synthesis, problems)
    return {
        "definer_outputs": {"persona_developer": result},
        "events": [make_event("agent_done", phase="definer", agent="persona_developer",
                              status="done", message=result["output"][:200])],
    }


def goal_setter_node(state: DoubleDiamondState) -> dict:
    personas = state["definer_outputs"].get("persona_developer", {}).get("output", "")
    problems = state["definer_outputs"].get("problem_definer", {}).get("output", "")
    result = _agent(GoalSetterAgent, state).run(state["brief"], personas, problems)
    return {
        "definer_outputs": {"goal_setter": result},
        "events": [make_event("agent_done", phase="definer", agent="goal_setter",
                              status="done", message=result["output"][:200])],
    }


def problem_framer_node(state: DoubleDiamondState) -> dict:
    personas = state["definer_outputs"].get("persona_developer", {}).get("output", "")
    problems = state["definer_outputs"].get("problem_definer", {}).get("output", "")
    goals = state["definer_outputs"].get("goal_setter", {}).get("output", "")
    result = _agent(ProblemFramerAgent, state).run(state["brief"], personas, problems, goals)
    memory_store.save_phase(state["session_id"], "definer", state["definer_outputs"])
    return {
        "definer_outputs": {"problem_framer": result},
        "events": [make_event("phase_start", phase="security_1", status="running",
                              message="Definer phase complete. Running Security Checkpoint 1.")],
    }


# ===========================================================================
# SECURITY CHECKPOINT 1
# ===========================================================================

def security_checkpoint_1(state: DoubleDiamondState) -> dict:
    agent = _agent(SecurityAgent, state)
    result = agent.check_problem_definition(
        brief=state["brief"],
        definer_outputs=state["definer_outputs"],
        strict_mode=settings.security_strict_mode,
    )
    memory_store.save(state["session_id"], "security_check_1", {
        "decision": result.decision.value,
        "risk_score": result.risk_score,
        "summary": result.summary,
    })
    return {
        "security_check_1": {
            "decision": result.decision.value,
            "risk_score": result.risk_score,
            "summary": result.summary,
            "findings": result.findings,
            "recommendations": result.recommendations,
            "blockers": result.blockers,
            "full_report": result.full_report,
        },
        "phase_statuses": {"security_1": result.decision.value},
        "events": [make_event(
            "security_check",
            phase="security_1",
            agent="security",
            status=result.decision.value,
            message=f"Security Check 1: {result.decision.value.upper()} — {result.summary}",
            data={"risk_score": result.risk_score, "blockers": result.blockers},
        )],
    }


def _route_security_1(state: DoubleDiamondState) -> str:
    decision = state.get("security_check_1", {}).get("decision", "rejected")
    if decision == SecurityDecision.REJECTED.value:
        return "end_with_rejection"
    return "creator_fan_out"


# ===========================================================================
# PHASE 3 — Creator Nodes (parallel via Send)
# ===========================================================================

def creator_fan_out(state: DoubleDiamondState) -> list[Send]:
    return [
        Send("ideation_node", state),
        Send("prototyping_node", state),
        Send("uiux_node", state),
        Send("code_dev_node", state),
        Send("ab_testing_node", state),
    ]


def _problem_frame(state: DoubleDiamondState) -> str:
    return state["definer_outputs"].get("problem_framer", {}).get("output", state["brief"])


def ideation_node(state: DoubleDiamondState) -> dict:
    result = _agent(IdeationAgent, state).run(state["brief"], _problem_frame(state))
    return {
        "creator_outputs": {"ideation": result},
        "events": [make_event("agent_done", phase="creator", agent="ideation",
                              status="done", message=result["output"][:200])],
    }


def prototyping_node(state: DoubleDiamondState) -> dict:
    result = _agent(PrototypingAgent, state).run(state["brief"], _problem_frame(state))
    return {
        "creator_outputs": {"prototyping": result},
        "events": [make_event("agent_done", phase="creator", agent="prototyping",
                              status="done", message=result["output"][:200])],
    }


def uiux_node(state: DoubleDiamondState) -> dict:
    personas = state["definer_outputs"].get("persona_developer", {}).get("output", "")
    result = _agent(UIUXAgent, state).run(state["brief"], _problem_frame(state), personas)
    return {
        "creator_outputs": {"uiux_design": result},
        "events": [make_event("agent_done", phase="creator", agent="uiux_design",
                              status="done", message=result["output"][:200])],
    }


def code_dev_node(state: DoubleDiamondState) -> dict:
    result = _agent(CodeDevelopmentAgent, state).run(state["brief"], _problem_frame(state))
    return {
        "creator_outputs": {"code_development": result},
        "events": [make_event("agent_done", phase="creator", agent="code_development",
                              status="done", message=result["output"][:200])],
    }


def ab_testing_node(state: DoubleDiamondState) -> dict:
    result = _agent(ABTestingAgent, state).run(state["brief"], _problem_frame(state))
    return {
        "creator_outputs": {"ab_testing": result},
        "events": [make_event("agent_done", phase="creator", agent="ab_testing",
                              status="done", message=result["output"][:200])],
    }


def creator_gather(state: DoubleDiamondState) -> dict:
    memory_store.save_phase(state["session_id"], "creator", state["creator_outputs"])
    return {
        "current_phase": "launch_ops",
        "phase_statuses": {"creator": "done", "launch_ops": "running"},
        "events": [make_event("phase_start", phase="launch_ops", status="running",
                              message="Creator phase complete. Starting Launch & Ops phase.")],
    }


# ===========================================================================
# PHASE 4 — Launch & Ops Nodes (sequential)
# ===========================================================================

def _tech_plan(state: DoubleDiamondState) -> str:
    return state["creator_outputs"].get("code_development", {}).get("output", "")


def _solution_brief(state: DoubleDiamondState) -> str:
    return state["creator_outputs"].get("ideation", {}).get("output", "")


def launch_orchestration_node(state: DoubleDiamondState) -> dict:
    result = _agent(LaunchOrchestrationAgent, state).run(
        state["brief"], _solution_brief(state), _tech_plan(state)
    )
    return {
        "launch_ops_outputs": {"launch_orchestration": result},
        "events": [make_event("agent_done", phase="launch_ops", agent="launch_orchestration",
                              status="done", message=result["output"][:200])],
    }


def governance_node(state: DoubleDiamondState) -> dict:
    launch = state["launch_ops_outputs"].get("launch_orchestration", {}).get("output", "")
    result = _agent(GovernanceAgent, state).run(state["brief"], _solution_brief(state), launch)
    return {
        "launch_ops_outputs": {"governance": result},
        "events": [make_event("agent_done", phase="launch_ops", agent="governance",
                              status="done", message=result["output"][:200])],
    }


def monitoring_node(state: DoubleDiamondState) -> dict:
    governance = state["launch_ops_outputs"].get("governance", {}).get("output", "")
    result = _agent(MonitoringAgent, state).run(state["brief"], _tech_plan(state), governance)
    return {
        "launch_ops_outputs": {"monitoring": result},
        "events": [make_event("agent_done", phase="launch_ops", agent="monitoring",
                              status="done", message=result["output"][:200])],
    }


def customer_support_node(state: DoubleDiamondState) -> dict:
    personas = state["definer_outputs"].get("persona_developer", {}).get("output", "")
    result = _agent(CustomerSupportAgent, state).run(state["brief"], personas, _solution_brief(state))
    return {
        "launch_ops_outputs": {"customer_support": result},
        "events": [make_event("agent_done", phase="launch_ops", agent="customer_support",
                              status="done", message=result["output"][:200])],
    }


def continuous_updates_node(state: DoubleDiamondState) -> dict:
    monitoring = state["launch_ops_outputs"].get("monitoring", {}).get("output", "")
    result = _agent(ContinuousUpdateAgent, state).run(state["brief"], _tech_plan(state), monitoring)
    memory_store.save_phase(state["session_id"], "launch_ops", state["launch_ops_outputs"])
    return {
        "launch_ops_outputs": {"continuous_updates": result},
        "events": [make_event("phase_start", phase="security_2", status="running",
                              message="Launch & Ops phase complete. Running Security Checkpoint 2.")],
    }


# ===========================================================================
# SECURITY CHECKPOINT 2
# ===========================================================================

def security_checkpoint_2(state: DoubleDiamondState) -> dict:
    agent = _agent(SecurityAgent, state)
    result = agent.check_solution(
        brief=state["brief"],
        creator_outputs=state["creator_outputs"],
        launch_outputs=state["launch_ops_outputs"],
        strict_mode=settings.security_strict_mode,
    )
    final_status = "completed" if result.decision != SecurityDecision.REJECTED else "rejected"
    memory_store.save(state["session_id"], "security_check_2", {
        "decision": result.decision.value,
        "risk_score": result.risk_score,
        "summary": result.summary,
    })
    memory_store.save(state["session_id"], "final_status", final_status)
    return {
        "security_check_2": {
            "decision": result.decision.value,
            "risk_score": result.risk_score,
            "summary": result.summary,
            "findings": result.findings,
            "recommendations": result.recommendations,
            "blockers": result.blockers,
            "full_report": result.full_report,
        },
        "current_phase": "done",
        "phase_statuses": {"security_2": result.decision.value},
        "events": [make_event(
            "security_check",
            phase="security_2",
            agent="security",
            status=result.decision.value,
            message=f"Security Check 2: {result.decision.value.upper()} — {result.summary}",
            data={"risk_score": result.risk_score, "blockers": result.blockers},
        ), make_event("pipeline_complete", phase="done", status=final_status,
                     message=f"Pipeline {final_status}.")],
    }


def end_with_rejection(state: DoubleDiamondState) -> dict:
    """Terminal node when Security Checkpoint 1 rejects the problem definition."""
    return {
        "current_phase": "done",
        "events": [make_event("pipeline_complete", phase="done", status="rejected",
                              message="Pipeline terminated by Security Checkpoint 1.")],
    }


# ===========================================================================
# Graph assembly
# ===========================================================================

def build_graph() -> StateGraph:
    g = StateGraph(DoubleDiamondState)

    # ---- Explorer phase -------------------------------------------------
    g.add_conditional_edges(START, explorer_fan_out, [
        "market_insights_node", "ethnographic_node", "competitive_node",
        "data_mining_node", "trend_scouting_node", "tech_spikes_node",
    ])
    for node in [market_insights_node, ethnographic_node, competitive_node,
                 data_mining_node, trend_scouting_node, tech_spikes_node]:
        g.add_node(node)
        g.add_edge(node.__name__, "explorer_gather")

    g.add_node(explorer_gather)

    # ---- Definer phase --------------------------------------------------
    g.add_node(data_synthesiser_node)
    g.add_node(problem_definer_node)
    g.add_node(persona_developer_node)
    g.add_node(goal_setter_node)
    g.add_node(problem_framer_node)

    g.add_edge("explorer_gather", "data_synthesiser_node")
    g.add_edge("data_synthesiser_node", "problem_definer_node")
    g.add_edge("problem_definer_node", "persona_developer_node")
    g.add_edge("persona_developer_node", "goal_setter_node")
    g.add_edge("goal_setter_node", "problem_framer_node")

    # ---- Security Checkpoint 1 ------------------------------------------
    g.add_node(security_checkpoint_1)
    g.add_node(end_with_rejection)
    g.add_edge("problem_framer_node", "security_checkpoint_1")
    g.add_conditional_edges(
        "security_checkpoint_1",
        _route_security_1,
        {"creator_fan_out": "creator_fan_out", "end_with_rejection": "end_with_rejection"},
    )
    g.add_edge("end_with_rejection", END)

    # ---- Creator phase --------------------------------------------------
    g.add_conditional_edges("creator_fan_out", creator_fan_out, [
        "ideation_node", "prototyping_node", "uiux_node", "code_dev_node", "ab_testing_node",
    ])
    # Need a virtual fan_out node
    g.add_node("creator_fan_out", lambda s: {})

    for node in [ideation_node, prototyping_node, uiux_node, code_dev_node, ab_testing_node]:
        g.add_node(node)
        g.add_edge(node.__name__, "creator_gather")

    g.add_node(creator_gather)

    # ---- Launch & Ops phase ---------------------------------------------
    g.add_node(launch_orchestration_node)
    g.add_node(governance_node)
    g.add_node(monitoring_node)
    g.add_node(customer_support_node)
    g.add_node(continuous_updates_node)

    g.add_edge("creator_gather", "launch_orchestration_node")
    g.add_edge("launch_orchestration_node", "governance_node")
    g.add_edge("governance_node", "monitoring_node")
    g.add_edge("monitoring_node", "customer_support_node")
    g.add_edge("customer_support_node", "continuous_updates_node")

    # ---- Security Checkpoint 2 ------------------------------------------
    g.add_node(security_checkpoint_2)
    g.add_edge("continuous_updates_node", "security_checkpoint_2")
    g.add_edge("security_checkpoint_2", END)

    return g


def compile_pipeline():
    """Compile the graph into an executable LangGraph runnable."""
    graph = build_graph()
    return graph.compile()


# Cached compiled pipeline
_pipeline = None


def get_pipeline():
    global _pipeline
    if _pipeline is None:
        _pipeline = compile_pipeline()
    return _pipeline
