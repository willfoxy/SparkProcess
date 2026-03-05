"""
Phase 4 — Launch & Ops Agents (Solution Space: Converge)

Five agents run SEQUENTIALLY to deliver, launch, and operate the solution.

Agents:
  1. LaunchOrchestrationAgent — In-life launch orchestration plan
  2. GovernanceAgent           — Automated governance & compliance
  3. MonitoringAgent           — Post-launch monitoring setup
  4. CustomerSupportAgent      — AI customer support design
  5. ContinuousUpdateAgent     — Continuous improvement pipeline
"""

from backend.agents.base import BaseAgent


class LaunchOrchestrationAgent(BaseAgent):
    role = "launch_orchestration"
    phase = "launch_ops"
    system = """You are a launch strategist and program manager with expertise in bringing products to market.
You create detailed, executable launch plans that account for every stakeholder and dependency.
You think in RACI, critical path, and risk mitigation."""

    def run(self, brief: str, solution_brief: str, tech_plan: str) -> dict:
        messages = [{"role": "user", "content": f"""
Original Brief: {brief}

Solution Brief:
{solution_brief}

Technical Implementation Plan:
{tech_plan}

Create a comprehensive launch orchestration plan:
1. **Launch Strategy**: Soft launch → beta → full launch phases
2. **Go-to-Market Plan**: Channels, messaging, pricing strategy
3. **Launch Checklist**: 40-point pre-launch checklist
4. **Stakeholder Map**: All teams, their roles, and dependencies (RACI)
5. **Critical Path**: Key milestones and dependencies (Gantt-style narrative)
6. **Risk Register**: Top 10 launch risks with mitigation plans
7. **Day-1 Runbook**: Hour-by-hour launch day playbook
"""}]
        return {
            "agent": self.role,
            "phase": self.phase,
            "output": self.invoke(messages),
        }


class GovernanceAgent(BaseAgent):
    role = "governance"
    phase = "launch_ops"
    system = """You are a governance, risk, and compliance (GRC) specialist with expertise in AI systems and digital products.
You design automated governance frameworks that protect without slowing progress.
You understand regulatory landscapes (GDPR, AI Act, SOC2, ISO27001) and best practices."""

    def run(self, brief: str, solution_brief: str, launch_plan: str) -> dict:
        messages = [{"role": "user", "content": f"""
Brief: {brief}

Solution Overview:
{solution_brief}

Launch Plan:
{launch_plan}

Design an automated governance and compliance framework:
1. **Regulatory Landscape**: Relevant regulations and compliance requirements
2. **AI Governance Controls**: Specific controls for AI/ML components
3. **Data Governance**: Data classification, retention, access controls
4. **Automated Compliance Checks**: What can be automated in CI/CD pipelines
5. **Audit Trail Requirements**: What needs to be logged and for how long
6. **Incident Response Playbook**: Steps when a governance issue is detected
7. **Ongoing Compliance Calendar**: Monthly/quarterly compliance activities
"""}]
        return {
            "agent": self.role,
            "phase": self.phase,
            "output": self.invoke(messages),
        }


class MonitoringAgent(BaseAgent):
    role = "monitoring"
    phase = "launch_ops"
    system = """You are an SRE (Site Reliability Engineer) and observability expert.
You design monitoring systems that catch issues before users do.
You think in SLOs, SLAs, error budgets, and runbooks."""

    def run(self, brief: str, tech_plan: str, governance: str) -> dict:
        messages = [{"role": "user", "content": f"""
Brief: {brief}

Technical Plan:
{tech_plan}

Governance Requirements:
{governance}

Design a comprehensive post-launch monitoring setup:
1. **Observability Stack**: Tools and platforms (metrics, logs, traces)
2. **SLOs & SLAs**: Service level objectives and agreements
3. **Key Dashboards**: 5 critical dashboards to build (describe what each shows)
4. **Alert Configuration**: Alert rules, thresholds, and escalation paths
5. **Business Metrics Monitoring**: Product analytics and KPI tracking
6. **AI Model Monitoring**: Drift detection, performance degradation, bias monitoring
7. **Incident Playbooks**: Top 5 incident scenarios with response steps
"""}]
        return {
            "agent": self.role,
            "phase": self.phase,
            "output": self.invoke(messages),
        }


class CustomerSupportAgent(BaseAgent):
    role = "customer_support"
    phase = "launch_ops"
    system = """You are a customer experience architect specialising in AI-powered support systems.
You design support ecosystems that delight customers and reduce operational costs.
You balance automation with human empathy."""

    def run(self, brief: str, personas: str, solution_brief: str) -> dict:
        messages = [{"role": "user", "content": f"""
Brief: {brief}

User Personas:
{personas}

Solution Overview:
{solution_brief}

Design an AI customer support system:
1. **Support Channel Strategy**: Which channels to offer and priority order
2. **AI Chatbot Design**: Conversation flows, intents, and escalation triggers
3. **Knowledge Base Architecture**: Structure and top 20 articles to create first
4. **Human Handoff Protocol**: When and how to escalate to humans
5. **Customer Feedback Loop**: How to capture and act on support insights
6. **Support Metrics**: CSAT, FRT, FCR targets and measurement approach
7. **Proactive Support Interventions**: How to help users before they need to ask
"""}]
        return {
            "agent": self.role,
            "phase": self.phase,
            "output": self.invoke(messages),
        }


class ContinuousUpdateAgent(BaseAgent):
    role = "continuous_updates"
    phase = "launch_ops"
    system = """You are a continuous delivery and product operations expert.
You design systems that allow teams to ship safely and often.
You are an expert in DevOps, CI/CD, feature flags, and product-led growth."""

    def run(self, brief: str, tech_plan: str, monitoring: str) -> dict:
        messages = [{"role": "user", "content": f"""
Brief: {brief}

Technical Plan:
{tech_plan}

Monitoring Setup:
{monitoring}

Design a continuous improvement and delivery pipeline:
1. **CI/CD Pipeline Design**: From commit to production (stages, gates, approvals)
2. **Feature Flag Strategy**: How to manage gradual rollouts and experiments
3. **Release Cadence**: Sprint schedule, release windows, and deployment frequency targets
4. **Feedback Integration**: How user feedback, analytics, and support data feed into roadmap
5. **Technical Debt Management**: How to balance new features with code quality
6. **AI Model Retraining Pipeline**: How to continuously improve ML components
7. **Product Metrics Reviews**: Weekly/monthly review cadence and decision framework
"""}]
        return {
            "agent": self.role,
            "phase": self.phase,
            "output": self.invoke(messages),
        }
