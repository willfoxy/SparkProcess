"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import type { AgentConfig, AgentStatus, PhaseConfig } from "@/types";

interface Props {
  agent: AgentConfig;
  phase: PhaseConfig;
  status: AgentStatus;
  output?: string;
}

const STATUS_LABELS: Record<AgentStatus, string> = {
  pending: "Waiting",
  running: "Running",
  done: "Complete",
  error: "Error",
};

export default function AgentCard({ agent, phase, status, output }: Props) {
  const [expanded, setExpanded] = useState(false);

  const isRunning = status === "running";
  const isDone = status === "done";
  const isPending = status === "pending";

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      className={`
        relative rounded-xl border overflow-hidden transition-all duration-300
        ${isDone ? `${phase.borderClass} ${phase.bgClass}` : "border-white/8 bg-white/2"}
        ${isRunning ? `${phase.borderClass} shadow-lg` : ""}
      `}
      style={isRunning ? { boxShadow: `0 0 20px ${phase.glowColor}` } : undefined}
    >
      {/* Running shimmer bar */}
      {isRunning && (
        <div className="absolute top-0 left-0 right-0 h-0.5 shimmer"
          style={{ background: `linear-gradient(90deg, transparent, ${phase.color}, transparent)` }} />
      )}

      <div
        className="flex items-center gap-3 p-3 cursor-pointer select-none"
        onClick={() => isDone && setExpanded((e) => !e)}
      >
        {/* Status indicator */}
        <div className="relative flex-shrink-0">
          <div className={`
            w-2.5 h-2.5 rounded-full transition-all duration-300
            ${isRunning ? "status-running" : ""}
          `}
            style={{
              backgroundColor: isPending
                ? "rgba(255,255,255,0.2)"
                : isRunning
                ? phase.color
                : isDone
                ? "#10B981"
                : "#EF4444",
              boxShadow: isRunning ? `0 0 8px ${phase.color}` : undefined,
            }}
          />
        </div>

        {/* Info */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <span className={`text-sm font-medium truncate ${isDone ? "text-white" : "text-slate-400"}`}>
              {agent.label}
            </span>
            {isDone && (
              <span className="text-xs px-1.5 py-0.5 rounded-full font-medium"
                style={{ backgroundColor: `${phase.color}20`, color: phase.color }}>
                Done
              </span>
            )}
            {isRunning && (
              <span className="text-xs px-1.5 py-0.5 rounded-full font-medium bg-white/10 text-white/70">
                Running…
              </span>
            )}
          </div>
          <p className="text-xs text-slate-500 truncate">{agent.description}</p>
        </div>

        {/* Expand toggle */}
        {isDone && output && (
          <motion.div
            animate={{ rotate: expanded ? 180 : 0 }}
            className="text-slate-500 flex-shrink-0"
          >
            <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
              <path d="M3 5l4 4 4-4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </motion.div>
        )}
      </div>

      {/* Output content */}
      <AnimatePresence>
        {expanded && isDone && output && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.25, ease: "easeInOut" }}
            className="overflow-hidden"
          >
            <div className="px-4 pb-4 pt-1 border-t border-white/5">
              <div className="max-h-96 overflow-y-auto pr-1">
                <div className="agent-prose">
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>
                    {output}
                  </ReactMarkdown>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Running placeholder */}
      {isRunning && (
        <div className="px-4 pb-3 pt-1">
          <div className="space-y-1.5">
            {[80, 65, 72, 55].map((w, i) => (
              <div key={i} className="h-2 rounded-full shimmer"
                style={{ width: `${w}%`, backgroundColor: `${phase.color}20` }} />
            ))}
          </div>
        </div>
      )}
    </motion.div>
  );
}
