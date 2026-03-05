"use client";

import { motion, AnimatePresence } from "framer-motion";
import { useState } from "react";
import type { SecurityCheck } from "@/types";

interface Props {
  checkpoint: "1" | "2";
  check: Partial<SecurityCheck> | null;
}

export default function SecurityBadge({ checkpoint, check }: Props) {
  const [open, setOpen] = useState(false);

  if (!check?.decision) return null;

  const d = check.decision;
  const colors = {
    approved: { bg: "bg-emerald-500/15", border: "border-emerald-500/40", text: "text-emerald-400", glow: "rgba(16,185,129,0.3)" },
    flagged:  { bg: "bg-amber-500/15",   border: "border-amber-500/40",   text: "text-amber-400",   glow: "rgba(245,158,11,0.3)" },
    rejected: { bg: "bg-red-500/15",     border: "border-red-500/40",     text: "text-red-400",     glow: "rgba(239,68,68,0.3)" },
  }[d] ?? { bg: "bg-white/5", border: "border-white/10", text: "text-white", glow: "transparent" };

  const icons = { approved: "✓", flagged: "⚑", rejected: "✗" };

  return (
    <div className="w-full">
      <motion.button
        onClick={() => setOpen((o) => !o)}
        className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl border ${colors.bg} ${colors.border} transition-all`}
        style={{ boxShadow: `0 0 16px ${colors.glow}` }}
        whileHover={{ scale: 1.01 }}
        whileTap={{ scale: 0.99 }}
      >
        <span className={`text-xl font-bold ${colors.text}`}>{icons[d]}</span>
        <div className="flex-1 text-left min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <span className={`text-sm font-semibold ${colors.text}`}>
              Security Check {checkpoint}
            </span>
            <span className={`text-xs px-2 py-0.5 rounded-full font-medium uppercase tracking-wide ${colors.bg} ${colors.text} border ${colors.border}`}>
              {d}
            </span>
            {check.risk_score !== undefined && (
              <span className="text-xs text-slate-400">
                Risk: {check.risk_score}/100
              </span>
            )}
          </div>
          {check.summary && (
            <p className="text-xs text-slate-400 truncate mt-0.5">{check.summary}</p>
          )}
        </div>
        <motion.span
          animate={{ rotate: open ? 180 : 0 }}
          className="text-slate-500 flex-shrink-0 text-xs"
        >
          ▼
        </motion.span>
      </motion.button>

      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="overflow-hidden"
          >
            <div className={`mt-2 rounded-xl border ${colors.border} ${colors.bg} p-4 space-y-3`}>
              {check.findings && check.findings.length > 0 && (
                <div>
                  <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
                    Findings
                  </h4>
                  <ul className="space-y-1">
                    {check.findings.map((f, i) => (
                      <li key={i} className="text-xs text-slate-400 flex items-start gap-2">
                        <span className="text-slate-600 mt-0.5">•</span>
                        <span>{f}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
              {check.blockers && check.blockers.length > 0 && (
                <div>
                  <h4 className="text-xs font-semibold text-red-400 uppercase tracking-wider mb-2">
                    Blockers
                  </h4>
                  <ul className="space-y-1">
                    {check.blockers.map((b, i) => (
                      <li key={i} className="text-xs text-red-300 flex items-start gap-2">
                        <span className="text-red-500 mt-0.5">✗</span>
                        <span>{b}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
