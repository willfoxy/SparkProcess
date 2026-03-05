"use client";

import { useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import type { PipelineEvent } from "@/types";

interface Props {
  events: PipelineEvent[];
}

const TYPE_STYLES: Record<string, { icon: string; color: string }> = {
  pipeline_start:    { icon: "▶", color: "text-blue-400" },
  pipeline_complete: { icon: "✓", color: "text-emerald-400" },
  phase_start:       { icon: "◆", color: "text-purple-400" },
  agent_start:       { icon: "→", color: "text-slate-400" },
  agent_done:        { icon: "●", color: "text-emerald-400" },
  security_check:    { icon: "⚑", color: "text-amber-400" },
  error:             { icon: "✗", color: "text-red-400" },
  snapshot:          { icon: "◉", color: "text-slate-500" },
};

export default function EventFeed({ events }: Props) {
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [events.length]);

  const visible = events
    .filter((e) => !["heartbeat", "snapshot", "stream_end"].includes(e.type))
    .slice(-50);

  return (
    <div className="rounded-xl border border-white/8 bg-white/2 overflow-hidden">
      <div className="px-4 py-2.5 border-b border-white/6 flex items-center gap-2">
        <div className="w-1.5 h-1.5 rounded-full bg-emerald-400 status-running" />
        <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
          Live Events
        </span>
        <span className="ml-auto text-xs text-slate-600">{events.length} total</span>
      </div>
      <div className="h-48 overflow-y-auto font-mono text-xs p-3 space-y-1">
        <AnimatePresence initial={false}>
          {visible.map((ev, i) => {
            const style = TYPE_STYLES[ev.type] ?? { icon: "·", color: "text-slate-500" };
            const time = ev.timestamp
              ? new Date(ev.timestamp).toLocaleTimeString("en-US", {
                  hour: "2-digit", minute: "2-digit", second: "2-digit",
                })
              : "";
            return (
              <motion.div
                key={`${ev.timestamp}-${i}`}
                initial={{ opacity: 0, x: -8 }}
                animate={{ opacity: 1, x: 0 }}
                className="flex items-start gap-2"
              >
                <span className={`${style.color} flex-shrink-0`}>{style.icon}</span>
                <span className="text-slate-600 flex-shrink-0">{time}</span>
                <span className="text-slate-300 break-words min-w-0">{ev.message}</span>
              </motion.div>
            );
          })}
        </AnimatePresence>
        <div ref={endRef} />
      </div>
    </div>
  );
}
