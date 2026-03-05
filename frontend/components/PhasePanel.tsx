"use client";

import { motion } from "framer-motion";
import type { AgentStatus, PhaseConfig, PhaseStatus } from "@/types";
import AgentCard from "./AgentCard";

interface Props {
  phase: PhaseConfig;
  status: PhaseStatus;
  agentStates: Record<string, { status: AgentStatus; output: string }>;
  isActive: boolean;
}

const STATUS_META: Record<PhaseStatus, { label: string; dotColor: string }> = {
  pending:  { label: "Waiting",  dotColor: "bg-slate-600" },
  running:  { label: "Running",  dotColor: "bg-blue-400 status-running" },
  done:     { label: "Done",     dotColor: "bg-emerald-400" },
  failed:   { label: "Failed",   dotColor: "bg-red-400" },
  approved: { label: "Approved", dotColor: "bg-emerald-400" },
  flagged:  { label: "Flagged",  dotColor: "bg-amber-400" },
  rejected: { label: "Rejected", dotColor: "bg-red-400" },
};

export default function PhasePanel({ phase, status, agentStates, isActive }: Props) {
  const meta = STATUS_META[status] ?? STATUS_META.pending;
  const doneCount = phase.agents.filter(
    (a) => agentStates[a.id]?.status === "done"
  ).length;

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      className={`
        rounded-2xl border overflow-hidden transition-all duration-500
        ${isActive ? `border-[${phase.color}]/30` : "border-white/6"}
      `}
      style={
        isActive
          ? {
              borderColor: `${phase.color}40`,
              boxShadow: `0 0 32px ${phase.glowColor}, 0 8px 32px rgba(0,0,0,0.5)`,
            }
          : { boxShadow: "0 4px 16px rgba(0,0,0,0.4)" }
      }
    >
      {/* Phase header */}
      <div
        className="px-4 py-3 flex items-center gap-3"
        style={{
          background: isActive
            ? `linear-gradient(135deg, ${phase.color}18, ${phase.color}08)`
            : "rgba(255,255,255,0.02)",
          borderBottom: "1px solid rgba(255,255,255,0.06)",
        }}
      >
        <span className="text-2xl">{phase.icon}</span>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <h3 className="font-semibold text-sm text-white">{phase.label}</h3>
            <span
              className="text-xs px-2 py-0.5 rounded-full font-medium"
              style={{ backgroundColor: `${phase.color}20`, color: phase.color }}
            >
              {doneCount}/{phase.agents.length}
            </span>
          </div>
          <p className="text-xs text-slate-500 truncate">{phase.description}</p>
        </div>
        {/* Status dot + label */}
        <div className="flex items-center gap-1.5 flex-shrink-0">
          <div className={`w-2 h-2 rounded-full ${meta.dotColor}`} />
          <span className="text-xs text-slate-400 hidden sm:block">{meta.label}</span>
        </div>
      </div>

      {/* Progress bar */}
      {(status === "running" || status === "done") && (
        <div className="h-0.5 bg-white/5">
          <motion.div
            className="h-full"
            style={{ backgroundColor: phase.color }}
            initial={{ width: 0 }}
            animate={{ width: `${(doneCount / phase.agents.length) * 100}%` }}
            transition={{ duration: 0.5 }}
          />
        </div>
      )}

      {/* Agent cards */}
      <div className="p-3 space-y-2">
        {phase.agents.map((agent) => {
          const agentState = agentStates[agent.id];
          const agentStatus: AgentStatus = agentState?.status ?? (
            status === "pending" ? "pending" :
            status === "running" ? "pending" :
            "pending"
          );
          return (
            <AgentCard
              key={agent.id}
              agent={agent}
              phase={phase}
              status={agentStatus}
              output={agentState?.output}
            />
          );
        })}
      </div>
    </motion.div>
  );
}
