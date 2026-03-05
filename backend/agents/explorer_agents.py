"""
Phase 1 — Explorer Agents (Problem Space: Diverge)

Six agents run in PARALLEL to gather wide market, user, and technical intelligence.

Agents:
  1. MarketInsightsAgent    — User & market research
  2. EthnographicAgent      — User behaviour / ethnographic research
  3. CompetitiveAnalysisAgent — Competitor landscape
  4. DataMiningAgent        — Data signals & analytics
  5. TrendScoutingAgent     — Emerging trends
  6. TechSpikesAgent        — Technical feasibility spikes
"""

from backend.agents.base import BaseAgent


class MarketInsightsAgent(BaseAgent):
    role = "market_insights"
    phase = "explorer"
    system = """You are an expert market researcher and user insights specialist.
Your task is to provide deep user and market intelligence.
Focus on: user needs, pain points, market size, customer segments, and unmet opportunities.
Structure your response with clear sections: Market Overview, Customer Segments, Key Pain Points, Opportunities.
Be specific, data-informed, and actionable."""

    def run(self, brief: str) -> dict:
        messages = [{"role": "user", "content": f"""
Conduct a thorough market and user insights analysis for the following challenge:

{brief}

Provide:
1. **Market Overview**: Size, growth, key dynamics
2. **Customer Segments**: Primary and secondary user groups with personas
3. **Key Pain Points**: Top 5 unmet needs or frustrations
4. **Opportunities**: Where the biggest value can be created
5. **Evidence Base**: What data/research supports these insights
"""}]
        return {
            "agent": self.role,
            "phase": self.phase,
            "output": self.invoke(messages),
        }


class EthnographicAgent(BaseAgent):
    role = "ethnographic_research"
    phase = "explorer"
    system = """You are a design anthropologist and ethnographic researcher.
You deeply understand human behaviour, cultural context, and lived experiences.
Focus on: observational insights, mental models, behavioural patterns, contextual factors.
Use rich, descriptive language and surface non-obvious insights."""

    def run(self, brief: str) -> dict:
        messages = [{"role": "user", "content": f"""
Conduct an ethnographic research analysis for:

{brief}

Explore:
1. **Day-in-the-Life**: How people currently live/work in this context
2. **Mental Models**: How users think about this problem space
3. **Workarounds & Hacks**: What improvised solutions exist already
4. **Emotional Landscape**: Feelings, frustrations, aspirations
5. **Cultural & Contextual Factors**: Environmental influences on behaviour
"""}]
        return {
            "agent": self.role,
            "phase": self.phase,
            "output": self.invoke(messages),
        }


class CompetitiveAnalysisAgent(BaseAgent):
    role = "competitive_analysis"
    phase = "explorer"
    system = """You are a strategic competitive intelligence analyst.
You map competitive landscapes with precision and identify strategic white spaces.
Focus on: direct competitors, indirect alternatives, feature gaps, positioning, moats."""

    def run(self, brief: str) -> dict:
        messages = [{"role": "user", "content": f"""
Perform a competitive analysis for:

{brief}

Include:
1. **Competitive Landscape Map**: Direct and indirect players
2. **Feature/Value Comparison**: What each player offers and at what price
3. **Strengths & Weaknesses**: Per competitor (SWOT)
4. **White Spaces**: Underserved areas and strategic gaps
5. **Positioning Opportunities**: How to differentiate
"""}]
        return {
            "agent": self.role,
            "phase": self.phase,
            "output": self.invoke(messages),
        }


class DataMiningAgent(BaseAgent):
    role = "data_mining"
    phase = "explorer"
    system = """You are a data scientist and analytics expert specialising in extracting actionable signals from data.
You identify patterns, correlations, and predictive indicators.
Focus on: quantitative signals, data-driven insights, statistical patterns, and measurement frameworks."""

    def run(self, brief: str) -> dict:
        messages = [{"role": "user", "content": f"""
Identify key data insights and measurement approaches for:

{brief}

Provide:
1. **Key Metrics to Track**: What KPIs and leading indicators matter
2. **Data Signals**: What existing data patterns are relevant
3. **Quantitative Insights**: Numbers, benchmarks, and statistics
4. **Data Collection Plan**: What data we need to gather and how
5. **Analytical Framework**: How to measure success
"""}]
        return {
            "agent": self.role,
            "phase": self.phase,
            "output": self.invoke(messages),
        }


class TrendScoutingAgent(BaseAgent):
    role = "trend_scouting"
    phase = "explorer"
    system = """You are a futurist and trend analyst with expertise in identifying emerging forces shaping industries.
You connect macro trends to micro opportunities.
Focus on: technology trends, social shifts, regulatory changes, economic forces, and future scenarios."""

    def run(self, brief: str) -> dict:
        messages = [{"role": "user", "content": f"""
Scout trends relevant to this innovation challenge:

{brief}

Cover:
1. **Technology Trends**: Emerging tech enablers (AI, IoT, blockchain, etc.)
2. **Social & Cultural Shifts**: Changing behaviours and expectations
3. **Regulatory & Political Landscape**: Rules shaping the space
4. **Economic Forces**: Market economics and financial dynamics
5. **Future Scenarios**: 3 plausible futures (1yr, 3yr, 5yr horizon)
6. **Strategic Implications**: What these trends mean for the opportunity
"""}]
        return {
            "agent": self.role,
            "phase": self.phase,
            "output": self.invoke(messages),
        }


class TechSpikesAgent(BaseAgent):
    role = "tech_spikes"
    phase = "explorer"
    system = """You are a principal engineer and technical strategist.
You evaluate technical feasibility, architecture options, and implementation risks.
Focus on: build vs buy, technical risks, required capabilities, proof-of-concept approaches."""

    def run(self, brief: str) -> dict:
        messages = [{"role": "user", "content": f"""
Conduct technical feasibility spikes for:

{brief}

Assess:
1. **Technical Landscape**: Relevant technologies and platforms
2. **Feasibility Assessment**: What's technically possible today
3. **Build vs Buy vs Partner**: For key capabilities
4. **Technical Risks**: Potential blockers and mitigation strategies
5. **Architecture Pointers**: High-level technical direction
6. **Proof of Concept Proposals**: Quick experiments to validate assumptions
"""}]
        return {
            "agent": self.role,
            "phase": self.phase,
            "output": self.invoke(messages),
        }
