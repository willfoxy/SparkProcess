export type Phase =
  | "explorer"
  | "definer"
  | "security_1"
  | "creator"
  | "launch_ops"
  | "security_2"
  | "done";

export type AgentStatus = "pending" | "running" | "done" | "error";
export type SecurityDecision = "approved" | "flagged" | "rejected";
export type PhaseStatus = "pending" | "running" | "done" | "failed" | SecurityDecision;

export interface AgentOutput {
  agent: string;
  phase: string;
  output: string;
}

export interface SecurityCheck {
  decision: SecurityDecision;
  risk_score: number;
  summary: string;
  findings: string[];
  recommendations: string[];
  blockers: string[];
  full_report: string;
}

export interface SessionSummary {
  session_id: string;
  brief: string;
  organization: string;
  created_at: string;
  current_phase: string;
  phase_statuses: Record<string, PhaseStatus>;
  security_check_1: Partial<SecurityCheck>;
  security_check_2: Partial<SecurityCheck>;
}

export interface SessionDetail extends SessionSummary {
  explorer_outputs: Record<string, AgentOutput>;
  definer_outputs: Record<string, AgentOutput>;
  creator_outputs: Record<string, AgentOutput>;
  launch_ops_outputs: Record<string, AgentOutput>;
  events: PipelineEvent[];
  errors: string[];
}

export interface PipelineEvent {
  type:
    | "pipeline_start"
    | "pipeline_complete"
    | "phase_start"
    | "agent_start"
    | "agent_done"
    | "security_check"
    | "snapshot"
    | "heartbeat"
    | "stream_end"
    | "error";
  phase: string;
  agent?: string;
  status: string;
  message: string;
  data: Record<string, unknown>;
  timestamp: string;
}

export interface PhaseConfig {
  id: Phase;
  label: string;
  description: string;
  color: string;
  glowColor: string;
  mutedColor: string;
  shadowClass: string;
  borderClass: string;
  bgClass: string;
  icon: string;
  agents: AgentConfig[];
}

export interface AgentConfig {
  id: string;
  label: string;
  description: string;
}

// ---------------------------------------------------------------------------
// Phase + Agent registry (used by the UI)
// ---------------------------------------------------------------------------

export const PHASE_CONFIGS: PhaseConfig[] = [
  {
    id: "explorer",
    label: "Explorer Agents",
    description: "User & Market Insights — Problem Space: Diverge",
    color: "#3B82F6",
    glowColor: "rgba(59,130,246,0.35)",
    mutedColor: "rgba(59,130,246,0.12)",
    shadowClass: "shadow-glow-blue",
    borderClass: "border-explorer/30",
    bgClass: "bg-explorer/10",
    icon: "🔭",
    agents: [
      { id: "market_insights", label: "Market Insights", description: "User & market research" },
      { id: "ethnographic_research", label: "Ethnographic Research", description: "User behaviour & culture" },
      { id: "competitive_analysis", label: "Competitive Analysis", description: "Competitor landscape" },
      { id: "data_mining", label: "Data Mining", description: "Data signals & analytics" },
      { id: "trend_scouting", label: "Trend Scouting", description: "Emerging trends & forces" },
      { id: "tech_spikes", label: "Tech Spikes", description: "Technical feasibility" },
    ],
  },
  {
    id: "definer",
    label: "Definer Agents",
    description: "Synthesise & Define — Problem Space: Converge",
    color: "#8B5CF6",
    glowColor: "rgba(139,92,246,0.35)",
    mutedColor: "rgba(139,92,246,0.12)",
    shadowClass: "shadow-glow-purple",
    borderClass: "border-definer/30",
    bgClass: "bg-definer/10",
    icon: "🎯",
    agents: [
      { id: "data_synthesiser", label: "Data Synthesiser", description: "Synthesise all findings" },
      { id: "problem_definer", label: "Problem Definer", description: "Define core problems" },
      { id: "persona_developer", label: "Persona Developer", description: "Develop user personas" },
      { id: "goal_setter", label: "Goal Setter", description: "Set strategic goals" },
      { id: "problem_framer", label: "Problem Framer", description: "HMW framing" },
    ],
  },
  {
    id: "creator",
    label: "Creator Agents",
    description: "Ideate Solutions — Solution Space: Diverge",
    color: "#EC4899",
    glowColor: "rgba(236,72,153,0.35)",
    mutedColor: "rgba(236,72,153,0.12)",
    shadowClass: "shadow-glow-pink",
    borderClass: "border-creator/30",
    bgClass: "bg-creator/10",
    icon: "⚡",
    agents: [
      { id: "ideation", label: "Ideation", description: "Generate diverse ideas" },
      { id: "prototyping", label: "Prototyping", description: "MVP & prototype plans" },
      { id: "uiux_design", label: "UI/UX Design", description: "Design concepts & flows" },
      { id: "code_development", label: "Code Development", description: "Technical implementation" },
      { id: "ab_testing", label: "A/B Testing", description: "Experiment design" },
    ],
  },
  {
    id: "launch_ops",
    label: "Launch & Ops",
    description: "Deliver & Operate — Solution Space: Converge",
    color: "#10B981",
    glowColor: "rgba(16,185,129,0.35)",
    mutedColor: "rgba(16,185,129,0.12)",
    shadowClass: "shadow-glow-green",
    borderClass: "border-launch/30",
    bgClass: "bg-launch/10",
    icon: "🚀",
    agents: [
      { id: "launch_orchestration", label: "Launch Orchestration", description: "Launch planning & GTM" },
      { id: "governance", label: "Governance", description: "Automated compliance" },
      { id: "monitoring", label: "Monitoring", description: "SLOs & observability" },
      { id: "customer_support", label: "Customer Support", description: "AI support design" },
      { id: "continuous_updates", label: "Continuous Updates", description: "CI/CD & improvement" },
    ],
  },
];
