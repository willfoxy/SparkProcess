"use client";

import { use, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import DiamondVisualization from "@/components/DiamondVisualization";
import PhasePanel from "@/components/PhasePanel";
import SecurityBadge from "@/components/SecurityBadge";
import EventFeed from "@/components/EventFeed";
import { useSessionStream } from "@/hooks/useSession";
import { getSession } from "@/lib/api";
import { PHASE_CONFIGS } from "@/types";
import type { Phase, SessionDetail } from "@/types";

interface Props {
  params: Promise<{ id: string }>;
}

export default function SessionPage({ params }: Props) {
  const { id } = use(params);
  const router = useRouter();
  const [activePhase, setActivePhase] = useState<Phase>("explorer");
  const [initialData, setInitialData] = useState<SessionDetail | null>(null);

  const stream = useSessionStream(id);

  // Load initial session data
  useEffect(() => {
    getSession(id).then(setInitialData).catch(() => router.replace("/"));
  }, [id]);

  const phaseStatuses = {
    ...initialData?.phase_statuses,
    ...stream.phaseStatuses,
  };
  const brief = initialData?.brief ?? "";
  const organization = initialData?.organization ?? "";

  // Build agentStates from stream + initial data
  const allOutputs = {
    ...initialData?.explorer_outputs,
    ...initialData?.definer_outputs,
    ...initialData?.creator_outputs,
    ...initialData?.launch_ops_outputs,
  };

  const agentStates: Record<string, { status: "pending" | "running" | "done" | "error"; output: string }> = {};
  for (const [key, val] of Object.entries(allOutputs)) {
    agentStates[key] = { status: "done", output: (val as { output: string }).output ?? "" };
  }
  for (const [key, val] of Object.entries(stream.agentStates)) {
    agentStates[key] = { status: val.status, output: val.output };
  }

  const currentPhase = stream.currentPhase || initialData?.current_phase || "explorer";
  const isComplete = stream.isComplete || currentPhase === "done";

  const securityCheck1 = stream.securityCheck1 ?? initialData?.security_check_1 ?? null;
  const securityCheck2 = stream.securityCheck2 ?? initialData?.security_check_2 ?? null;

  const events = [...(initialData?.events ?? []), ...stream.events];

  return (
    <div className="relative min-h-dvh grid-bg">
      {/* Background glows */}
      <div className="pointer-events-none fixed inset-0 overflow-hidden">
        <div className="absolute -top-40 -left-40 w-96 h-96 rounded-full bg-blue-600/8 blur-[100px]" />
        <div className="absolute top-1/2 right-0 w-80 h-80 rounded-full bg-purple-600/6 blur-[100px]" />
      </div>

      <div className="relative z-10 flex flex-col min-h-dvh">
        {/* Header */}
        <header className="sticky top-0 z-20 flex items-center gap-3 px-4 sm:px-6 py-3.5 border-b border-white/6 bg-bg-deep/80 backdrop-blur-xl">
          <button
            onClick={() => router.push("/")}
            className="text-slate-400 hover:text-white transition-colors flex-shrink-0"
            aria-label="Back"
          >
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
              <path d="M12 4l-6 6 6 6" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </button>
          <div className="flex items-center gap-2 flex-1 min-w-0">
            <div className="w-6 h-6 rounded-md bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-xs font-bold flex-shrink-0">
              ⚡
            </div>
            <div className="min-w-0">
              <p className="text-sm font-semibold text-white truncate leading-tight">
                {organization ? `${organization} · ` : ""}{brief.slice(0, 60)}{brief.length > 60 ? "…" : ""}
              </p>
            </div>
          </div>
          {/* Status pill */}
          <div className="flex items-center gap-1.5 flex-shrink-0">
            <div className={`w-2 h-2 rounded-full ${isComplete ? "bg-emerald-400" : "bg-blue-400 status-running"}`} />
            <span className="text-xs text-slate-400 hidden sm:block">
              {isComplete ? "Complete" : `Running: ${currentPhase}`}
            </span>
          </div>
        </header>

        <div className="flex-1 flex flex-col lg:flex-row gap-0">
          {/* Left: visualization + events sidebar */}
          <aside className="lg:w-80 xl:w-96 flex-shrink-0 border-b lg:border-b-0 lg:border-r border-white/6 p-4 space-y-4">
            {/* Diamond */}
            <div>
              <h2 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2 px-1">
                Pipeline
              </h2>
              <DiamondVisualization
                phaseStatuses={phaseStatuses}
                currentPhase={currentPhase}
                onPhaseClick={setActivePhase}
              />
            </div>

            {/* Phase quick nav */}
            <div>
              <h2 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2 px-1">
                Phases
              </h2>
              <div className="space-y-1">
                {PHASE_CONFIGS.map((phase) => {
                  const st = phaseStatuses[phase.id] ?? "pending";
                  return (
                    <button
                      key={phase.id}
                      onClick={() => setActivePhase(phase.id)}
                      className={`
                        w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-left transition-all
                        ${activePhase === phase.id ? "bg-white/8 border border-white/10" : "hover:bg-white/4"}
                      `}
                    >
                      <span className="text-base">{phase.icon}</span>
                      <span className="flex-1 text-sm text-slate-300 truncate">{phase.label}</span>
                      <span
                        className="w-2 h-2 rounded-full flex-shrink-0"
                        style={{
                          backgroundColor:
                            st === "pending" ? "rgba(255,255,255,0.15)" :
                            st === "running" ? phase.color :
                            st === "done" || st === "approved" ? "#10B981" :
                            st === "flagged" ? "#F59E0B" : "#EF4444",
                        }}
                      />
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Security badges */}
            {(securityCheck1?.decision || securityCheck2?.decision) && (
              <div className="space-y-2">
                <h2 className="text-xs font-semibold text-slate-500 uppercase tracking-wider px-1">
                  Security
                </h2>
                {securityCheck1?.decision && (
                  <SecurityBadge checkpoint="1" check={securityCheck1} />
                )}
                {securityCheck2?.decision && (
                  <SecurityBadge checkpoint="2" check={securityCheck2} />
                )}
              </div>
            )}

            {/* Events */}
            <EventFeed events={events} />
          </aside>

          {/* Main content: phase panels */}
          <main className="flex-1 p-4 overflow-y-auto">
            <AnimatePresence mode="wait">
              <motion.div
                key={activePhase}
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -8 }}
                transition={{ duration: 0.2 }}
              >
                {PHASE_CONFIGS.filter((p) => p.id === activePhase).map((phase) => (
                  <PhasePanel
                    key={phase.id}
                    phase={phase}
                    status={phaseStatuses[phase.id] ?? "pending"}
                    agentStates={agentStates}
                    isActive={currentPhase === phase.id}
                  />
                ))}
              </motion.div>
            </AnimatePresence>

            {/* All phases overview (mobile-friendly scrollable row) */}
            <div className="mt-6 hidden lg:block">
              <h2 className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-3">
                All Phases
              </h2>
              <div className="grid grid-cols-2 xl:grid-cols-2 gap-4">
                {PHASE_CONFIGS.filter((p) => p.id !== activePhase).map((phase) => (
                  <PhasePanel
                    key={phase.id}
                    phase={phase}
                    status={phaseStatuses[phase.id] ?? "pending"}
                    agentStates={agentStates}
                    isActive={false}
                  />
                ))}
              </div>
            </div>

            {/* Completion banner */}
            {isComplete && (
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className="mt-6 rounded-2xl border border-emerald-500/30 bg-emerald-500/8 p-6 text-center"
                style={{ boxShadow: "0 0 32px rgba(16,185,129,0.2)" }}
              >
                <div className="text-3xl mb-2">🎉</div>
                <h3 className="text-lg font-bold text-emerald-400 mb-1">
                  Pipeline Complete
                </h3>
                <p className="text-sm text-slate-400">
                  All {21} agents have finished. Your innovation brief has been fully processed
                  through the Double Diamond.
                </p>
              </motion.div>
            )}
          </main>
        </div>
      </div>
    </div>
  );
}
