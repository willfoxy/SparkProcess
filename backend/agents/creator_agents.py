"""
Phase 3 — Creator Agents (Solution Space: Diverge)

Five agents run in PARALLEL to generate, prototype, and test a wide
range of solution concepts.

Agents:
  1. IdeationAgent       — Generate diverse solution ideas
  2. PrototypingAgent    — Define MVPs and prototype plans
  3. UIUXAgent           — UI/UX design concepts
  4. CodeDevelopmentAgent — Technical implementation plans
  5. ABTestingAgent      — A/B test and experiment designs
"""

from backend.agents.base import BaseAgent


class IdeationAgent(BaseAgent):
    role = "ideation"
    phase = "creator"
    system = """You are a creative innovation catalyst who generates breakthrough solution ideas.
You combine divergent and convergent thinking.
No idea is too bold. Every idea is grounded in the problem space.
You use techniques like SCAMPER, analogical thinking, and first-principles reasoning."""

    def run(self, brief: str, problem_frame: str) -> dict:
        messages = [{"role": "user", "content": f"""
Brief: {brief}

Problem Frame & HMW Questions:
{problem_frame}

Generate a rich portfolio of solution ideas:
1. **10 Initial Concepts**: Diverse ideas across the solution space
2. **3 Wild Cards**: Unconventional, disruptive approaches
3. **Analogous Solutions**: What other industries have done for similar problems
4. **Technology-Enabled Ideas**: Solutions uniquely enabled by modern tech (AI, IoT, etc.)
5. **Top 3 Prioritised Concepts**: Best ideas ranked with rationale
6. **Concept Descriptions**: 1-paragraph description of each top concept including value proposition
"""}]
        return {
            "agent": self.role,
            "phase": self.phase,
            "output": self.invoke(messages),
        }


class PrototypingAgent(BaseAgent):
    role = "prototyping"
    phase = "creator"
    system = """You are a rapid prototyping expert and lean startup practitioner.
You design MVPs that maximise learning while minimising investment.
Every prototype has a clear hypothesis and success criteria."""

    def run(self, brief: str, problem_frame: str) -> dict:
        messages = [{"role": "user", "content": f"""
Brief: {brief}

Problem Frame:
{problem_frame}

Design a prototyping and MVP strategy:
1. **Prototype Ladder**: 5 prototypes from paper sketch to working MVP
2. **MVP Definition**: What the minimum viable product includes (and excludes)
3. **Prototype Hypotheses**: Key assumptions each prototype tests
4. **Build Plan**: Sprint-by-sprint prototype roadmap (8 weeks)
5. **User Testing Protocol**: How to test each prototype with users
6. **Go/No-Go Criteria**: What results would validate or invalidate each concept
"""}]
        return {
            "agent": self.role,
            "phase": self.phase,
            "output": self.invoke(messages),
        }


class UIUXAgent(BaseAgent):
    role = "uiux_design"
    phase = "creator"
    system = """You are a world-class UX designer and design systems expert.
You create intuitive, beautiful, and accessible interfaces.
You think in user journeys, information architecture, and interaction patterns."""

    def run(self, brief: str, problem_frame: str, personas: str) -> dict:
        messages = [{"role": "user", "content": f"""
Brief: {brief}

Problem Frame:
{problem_frame}

User Personas:
{personas}

Generate UI/UX design concepts:
1. **Core User Journey**: End-to-end flow for the primary persona
2. **Information Architecture**: Site map / app structure
3. **Key Screen Descriptions**: Detailed description of 5 critical screens/views
4. **Design System Tokens**: Colours, typography, spacing, component philosophy
5. **Interaction Patterns**: Key micro-interactions and transitions
6. **Accessibility Considerations**: How to make it inclusive
7. **Mobile-First Approach**: How the experience adapts across devices
"""}]
        return {
            "agent": self.role,
            "phase": self.phase,
            "output": self.invoke(messages),
        }


class CodeDevelopmentAgent(BaseAgent):
    role = "code_development"
    phase = "creator"
    system = """You are a senior software architect who designs scalable, maintainable systems.
You make clear technology choices with strong rationale.
You balance speed-to-market with technical excellence."""

    def run(self, brief: str, problem_frame: str) -> dict:
        messages = [{"role": "user", "content": f"""
Brief: {brief}

Problem Frame:
{problem_frame}

Design the technical implementation:
1. **Architecture Decision**: Monolith vs microservices vs serverless rationale
2. **Tech Stack Recommendation**: Frontend, backend, database, infrastructure
3. **System Design**: Key components, APIs, data flows (describe as if drawing a diagram)
4. **Data Model**: Core entities and relationships
5. **API Design**: Key endpoints with request/response shapes
6. **Development Phases**: Phase 1 (MVP), Phase 2 (growth), Phase 3 (scale)
7. **Non-Functional Requirements**: Performance, security, scalability targets
"""}]
        return {
            "agent": self.role,
            "phase": self.phase,
            "output": self.invoke(messages),
        }


class ABTestingAgent(BaseAgent):
    role = "ab_testing"
    phase = "creator"
    system = """You are a growth engineer and experimentation expert.
You design rigorous A/B tests and experiment programmes that drive evidence-based decisions.
Every experiment has clear hypotheses, metrics, and sample size calculations."""

    def run(self, brief: str, problem_frame: str) -> dict:
        messages = [{"role": "user", "content": f"""
Brief: {brief}

Problem Frame:
{problem_frame}

Design an experimentation programme:
1. **Experimentation Roadmap**: 10 experiments in priority order
2. **Top 3 A/B Test Designs**: Full spec including:
   - Hypothesis (If X then Y because Z)
   - Control vs variant
   - Primary metric + guardrail metrics
   - Sample size estimate
   - Test duration
3. **Multivariate Tests**: Where multiple variables should be tested together
4. **Qualitative Experiments**: User interviews, usability tests, diary studies
5. **Learning Agenda**: What decisions each experiment informs
6. **Experimentation Infrastructure**: Tools and processes needed
"""}]
        return {
            "agent": self.role,
            "phase": self.phase,
            "output": self.invoke(messages),
        }
