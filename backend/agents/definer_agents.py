"""
Phase 2 — Definer Agents (Problem Space: Converge)

Five agents run SEQUENTIALLY to synthesise explorer intelligence into
a sharp, validated problem definition.

Agents:
  1. DataSynthesiserAgent   — Synthesise all explorer findings
  2. ProblemDefinerAgent    — Define the core problem(s)
  3. PersonaDeveloperAgent  — Develop user personas
  4. GoalSetterAgent        — Set strategic goals
  5. ProblemFramerAgent     — Frame the final problem statement (HMW)
"""

from backend.agents.base import BaseAgent


class DataSynthesiserAgent(BaseAgent):
    role = "data_synthesiser"
    phase = "definer"
    system = """You are a synthesis expert who transforms raw research into clear strategic insights.
You excel at pattern recognition, theming, and distilling complexity into clarity.
Output must be structured, prioritised, and actionable."""

    def run(self, brief: str, explorer_outputs: dict) -> dict:
        combined = "\n\n---\n\n".join(
            f"## {k.replace('_', ' ').title()}\n{v.get('output', '')}"
            for k, v in explorer_outputs.items()
        )
        messages = [{"role": "user", "content": f"""
Original Brief: {brief}

Explorer Research Findings:
{combined}

Synthesise all explorer findings into:
1. **Top 10 Key Insights**: Most important discoveries across all research
2. **Recurring Themes**: Patterns that appear across multiple research streams
3. **Tensions & Paradoxes**: Contradictions that need to be resolved
4. **Critical Unknowns**: What we still don't know
5. **Strategic Implications**: What this means for the innovation opportunity
"""}]
        return {
            "agent": self.role,
            "phase": self.phase,
            "output": self.invoke(messages),
        }


class ProblemDefinerAgent(BaseAgent):
    role = "problem_definer"
    phase = "definer"
    system = """You are a problem definition specialist who transforms messy research into crisp problem statements.
You distinguish root causes from symptoms and prioritise ruthlessly.
Every problem statement you write is specific, meaningful, and solvable."""

    def run(self, brief: str, synthesis: str) -> dict:
        messages = [{"role": "user", "content": f"""
Brief: {brief}

Synthesised Insights:
{synthesis}

Define the core problems:
1. **Root Cause Analysis**: What are the underlying causes (not symptoms)?
2. **Problem Hierarchy**: Primary, secondary, and tertiary problems
3. **Top 3 Core Problems**: The most critical problems to solve (ranked)
4. **Problem Validation**: Evidence that supports each problem definition
5. **Scope Boundaries**: What is in and out of scope
"""}]
        return {
            "agent": self.role,
            "phase": self.phase,
            "output": self.invoke(messages),
        }


class PersonaDeveloperAgent(BaseAgent):
    role = "persona_developer"
    phase = "definer"
    system = """You are a UX researcher and persona design expert.
You craft evidence-based user personas that capture goals, behaviours, and contexts.
Each persona is vivid, specific, and grounded in real research signals."""

    def run(self, brief: str, synthesis: str, problems: str) -> dict:
        messages = [{"role": "user", "content": f"""
Brief: {brief}

Synthesised Research:
{synthesis}

Core Problems:
{problems}

Develop 3 detailed user personas:
Each persona must include:
- Name & demographic snapshot
- Goals and motivations
- Frustrations and pain points
- Current behaviour and workarounds
- Relationship to the core problems
- Quote that captures their perspective
- Needs that a solution must address
"""}]
        return {
            "agent": self.role,
            "phase": self.phase,
            "output": self.invoke(messages),
        }


class GoalSetterAgent(BaseAgent):
    role = "goal_setter"
    phase = "definer"
    system = """You are a strategic goal-setting expert who bridges user needs and business objectives.
You write SMART goals that are ambitious yet achievable.
Every goal connects user value to business value."""

    def run(self, brief: str, personas: str, problems: str) -> dict:
        messages = [{"role": "user", "content": f"""
Brief: {brief}

User Personas:
{personas}

Core Problems:
{problems}

Define strategic goals:
1. **Vision Statement**: The north star (1 sentence)
2. **User Goals**: What success looks like for each persona
3. **Business Goals**: Revenue, growth, efficiency metrics
4. **Strategic Goals**: 5 SMART goals that bridge user + business value
5. **Success Metrics**: How we'll measure progress (OKRs format)
6. **Constraints**: Non-negotiables and guardrails
"""}]
        return {
            "agent": self.role,
            "phase": self.phase,
            "output": self.invoke(messages),
        }


class ProblemFramerAgent(BaseAgent):
    role = "problem_framer"
    phase = "definer"
    system = """You are a design thinking facilitator and problem framing expert.
You craft How Might We (HMW) questions and point-of-view statements that unlock creative solutions.
Your framings are specific enough to guide design but broad enough to allow innovation."""

    def run(self, brief: str, personas: str, problems: str, goals: str) -> dict:
        messages = [{"role": "user", "content": f"""
Brief: {brief}

User Personas:
{personas}

Core Problems:
{problems}

Strategic Goals:
{goals}

Frame the problem for the creative phase:
1. **Point of View Statements**: One per persona (user + need + insight format)
2. **How Might We Questions**: 10 HMW questions at different levels of abstraction
3. **Design Principles**: 5 principles that should guide all solutions
4. **Solution Space Brief**: Clear direction for the creator agents
5. **Evaluation Criteria**: How we'll judge solution ideas
"""}]
        return {
            "agent": self.role,
            "phase": self.phase,
            "output": self.invoke(messages),
        }
