"use client";

import { motion } from "framer-motion";
import type { Phase, PhaseStatus } from "@/types";

interface Props {
  phaseStatuses: Record<string, PhaseStatus>;
  currentPhase: string;
  onPhaseClick?: (phase: Phase) => void;
}

const PHASES = [
  { id: "explorer",  x: 120,  color: "#3B82F6", label: "Explorer" },
  { id: "definer",   x: 300,  color: "#8B5CF6", label: "Definer" },
  { id: "creator",   x: 500,  color: "#EC4899", label: "Creator" },
  { id: "launch_ops",x: 680,  color: "#10B981", label: "Launch" },
];

const SEC_POINTS = [
  { x: 400, label: "SEC 1", color: "#F59E0B" },
  { x: 790, label: "SEC 2", color: "#F59E0B" },
];

function statusColor(status?: PhaseStatus): string {
  if (!status || status === "pending") return "rgba(255,255,255,0.15)";
  if (status === "running") return "rgba(255,255,255,0.6)";
  if (status === "done" || status === "approved") return "#10B981";
  if (status === "flagged") return "#F59E0B";
  if (status === "rejected" || status === "failed") return "#EF4444";
  return "rgba(255,255,255,0.6)";
}

export default function DiamondVisualization({ phaseStatuses, currentPhase, onPhaseClick }: Props) {
  const W = 900;
  const H = 200;
  const mid = H / 2;
  const spread = 70;

  // Diamond paths
  const p1 = `M 60 ${mid} L 240 ${mid - spread} L 360 ${mid} L 240 ${mid + spread} Z`;
  const p2 = `M 360 ${mid} L 440 ${mid - spread} L 520 ${mid} L 440 ${mid + spread} Z`;
  const p3 = `M 520 ${mid} L 640 ${mid - spread} L 760 ${mid} L 640 ${mid + spread} Z`;
  const p4 = `M 760 ${mid} L 800 ${mid}`;

  return (
    <div className="w-full overflow-x-auto py-2">
      <svg
        viewBox={`0 0 ${W} ${H}`}
        className="w-full max-w-4xl mx-auto"
        style={{ minWidth: 480 }}
      >
        <defs>
          {/* Glow filters */}
          {["blue","purple","pink","green","amber"].map((c, i) => {
            const cols = ["59,130,246","139,92,246","236,72,153","16,185,129","245,158,11"];
            return (
              <filter key={c} id={`glow-${c}`}>
                <feGaussianBlur stdDeviation="3" result="blur" />
                <feFlood floodColor={`rgba(${cols[i]},0.8)`} result="color" />
                <feComposite in="color" in2="blur" operator="in" result="shadow" />
                <feMerge><feMergeNode in="shadow" /><feMergeNode in="SourceGraphic" /></feMerge>
              </filter>
            );
          })}
          {/* Flow animation gradient */}
          <linearGradient id="flowGrad" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="rgba(59,130,246,0)" />
            <stop offset="50%" stopColor="rgba(59,130,246,0.8)" />
            <stop offset="100%" stopColor="rgba(236,72,153,0)" />
          </linearGradient>
        </defs>

        {/* Background connecting line */}
        <line x1="60" y1={mid} x2={W - 60} y2={mid}
          stroke="rgba(255,255,255,0.06)" strokeWidth="2" strokeDasharray="6 4" />

        {/* Animated flow line (when running) */}
        {currentPhase !== "done" && (
          <motion.line
            x1="60" y1={mid} x2={W - 60} y2={mid}
            stroke="url(#flowGrad)"
            strokeWidth="2"
            initial={{ opacity: 0 }}
            animate={{ opacity: [0.3, 1, 0.3] }}
            transition={{ duration: 2, repeat: Infinity }}
          />
        )}

        {/* Diamond 1: Explorer */}
        <motion.path
          d={p1}
          fill={`rgba(59,130,246,${phaseStatuses.explorer === "running" ? 0.18 : 0.08})`}
          stroke={statusColor(phaseStatuses.explorer)}
          strokeWidth="1.5"
          filter={phaseStatuses.explorer === "running" ? "url(#glow-blue)" : undefined}
          whileHover={{ scale: 1.02 }}
          style={{ cursor: "pointer", transformOrigin: "240px 100px" }}
          onClick={() => onPhaseClick?.("explorer")}
        />
        {/* Diamond 2: Definer (smaller, converge) */}
        <motion.path
          d={p2}
          fill={`rgba(139,92,246,${phaseStatuses.definer === "running" ? 0.18 : 0.08})`}
          stroke={statusColor(phaseStatuses.definer)}
          strokeWidth="1.5"
          filter={phaseStatuses.definer === "running" ? "url(#glow-purple)" : undefined}
          style={{ cursor: "pointer", transformOrigin: "440px 100px" }}
          onClick={() => onPhaseClick?.("definer")}
        />
        {/* Diamond 3: Creator */}
        <motion.path
          d={p3}
          fill={`rgba(236,72,153,${phaseStatuses.creator === "running" ? 0.18 : 0.08})`}
          stroke={statusColor(phaseStatuses.creator)}
          strokeWidth="1.5"
          filter={phaseStatuses.creator === "running" ? "url(#glow-pink)" : undefined}
          style={{ cursor: "pointer", transformOrigin: "640px 100px" }}
          onClick={() => onPhaseClick?.("creator")}
        />
        {/* Diamond 4: Launch (arrow out) */}
        <motion.path
          d={`M 760 ${mid} L 840 ${mid - 30} L 860 ${mid} L 840 ${mid + 30} Z`}
          fill={`rgba(16,185,129,${phaseStatuses.launch_ops === "running" ? 0.18 : 0.08})`}
          stroke={statusColor(phaseStatuses.launch_ops)}
          strokeWidth="1.5"
          filter={phaseStatuses.launch_ops === "running" ? "url(#glow-green)" : undefined}
          style={{ cursor: "pointer", transformOrigin: "810px 100px" }}
          onClick={() => onPhaseClick?.("launch_ops")}
        />

        {/* Security checkpoint dots */}
        {SEC_POINTS.map((sp, i) => {
          const key = i === 0 ? "security_1" : "security_2";
          const st = phaseStatuses[key];
          return (
            <g key={sp.x}>
              <motion.circle
                cx={sp.x} cy={mid} r="8"
                fill={statusColor(st)}
                stroke={sp.color}
                strokeWidth="2"
                filter="url(#glow-amber)"
                animate={st === "running" ? { r: [8, 11, 8] } : {}}
                transition={{ duration: 1.5, repeat: Infinity }}
              />
              <text x={sp.x} y={mid + 24} textAnchor="middle"
                fill={sp.color} fontSize="9" fontWeight="600" letterSpacing="0.05em">
                {sp.label}
              </text>
            </g>
          );
        })}

        {/* Phase labels */}
        {[
          { x: 240, label: "EXPLORER", y: mid - spread - 14, color: "#3B82F6" },
          { x: 440, label: "DEFINER",  y: mid - spread - 14, color: "#8B5CF6" },
          { x: 640, label: "CREATOR",  y: mid - spread - 14, color: "#EC4899" },
          { x: 810, label: "LAUNCH",   y: mid - spread - 14, color: "#10B981" },
        ].map((lbl) => (
          <text key={lbl.label} x={lbl.x} y={lbl.y}
            textAnchor="middle" fill={lbl.color}
            fontSize="10" fontWeight="700" letterSpacing="0.08em" opacity="0.9">
            {lbl.label}
          </text>
        ))}

        {/* Problem Space / Solution Space labels */}
        <text x={300} y={H - 8} textAnchor="middle"
          fill="rgba(255,255,255,0.25)" fontSize="10" letterSpacing="0.05em">
          PROBLEM SPACE
        </text>
        <text x={650} y={H - 8} textAnchor="middle"
          fill="rgba(255,255,255,0.25)" fontSize="10" letterSpacing="0.05em">
          SOLUTION SPACE
        </text>

        {/* Input arrow */}
        <path d={`M 20 ${mid} L 55 ${mid}`}
          stroke="rgba(255,255,255,0.3)" strokeWidth="2"
          markerEnd="url(#arrow)" />
        <defs>
          <marker id="arrow" viewBox="0 0 10 10" refX="10" refY="5"
            markerWidth="6" markerHeight="6" orient="auto">
            <path d="M 0 0 L 10 5 L 0 10 z" fill="rgba(255,255,255,0.3)" />
          </marker>
        </defs>
        <text x="15" y={mid - 8} fill="rgba(255,255,255,0.3)" fontSize="8">BRIEF</text>

        {/* Output arrow */}
        <path d={`M 865 ${mid} L 890 ${mid}`}
          stroke="rgba(255,255,255,0.3)" strokeWidth="2"
          markerEnd="url(#arrow)" />
        <text x="868" y={mid - 8} fill="rgba(255,255,255,0.3)" fontSize="8">LAUNCH</text>
      </svg>
    </div>
  );
}
