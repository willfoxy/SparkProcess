"use client";

import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import SessionForm from "@/components/SessionForm";
import DiamondVisualization from "@/components/DiamondVisualization";

export default function HomePage() {
  const router = useRouter();

  function handleCreated(sessionId: string) {
    router.push(`/session/${sessionId}`);
  }

  return (
    <div className="relative min-h-dvh grid-bg overflow-hidden">
      {/* Background glows */}
      <div className="pointer-events-none fixed inset-0 overflow-hidden">
        <div className="absolute -top-40 -left-40 w-96 h-96 rounded-full bg-blue-600/10 blur-[100px]" />
        <div className="absolute -top-20 right-0 w-80 h-80 rounded-full bg-purple-600/8 blur-[100px]" />
        <div className="absolute bottom-0 left-1/3 w-96 h-60 rounded-full bg-pink-600/6 blur-[120px]" />
      </div>

      <div className="relative z-10 flex flex-col min-h-dvh">
        {/* Nav */}
        <header className="flex items-center justify-between px-6 py-4 border-b border-white/5">
          <div className="flex items-center gap-2.5">
            <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-sm font-bold">
              ⚡
            </div>
            <span className="font-bold text-white text-sm tracking-tight">SparkProcess</span>
          </div>
          <div className="flex items-center gap-4 text-xs text-slate-500">
            <span className="hidden sm:block">LangGraph + AWS Bedrock + Datadog</span>
            <a
              href="https://github.com"
              className="text-slate-400 hover:text-white transition-colors"
              target="_blank" rel="noopener noreferrer"
            >
              GitHub
            </a>
          </div>
        </header>

        {/* Hero */}
        <main className="flex-1 flex flex-col items-center justify-center px-4 py-12">
          <motion.div
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, ease: "easeOut" }}
            className="text-center max-w-3xl mx-auto mb-10"
          >
            {/* Badge */}
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.1 }}
              className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full border border-blue-500/30 bg-blue-500/8 text-blue-400 text-xs font-medium mb-6"
            >
              <span className="w-1.5 h-1.5 rounded-full bg-blue-400 status-running" />
              Autonomous AI Innovation Process
            </motion.div>

            <h1 className="text-4xl sm:text-5xl md:text-6xl font-bold text-white leading-tight mb-4">
              Double Diamond{" "}
              <span className="bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
                AI Orchestration
              </span>
            </h1>

            <p className="text-slate-400 text-lg max-w-xl mx-auto leading-relaxed">
              21 specialist AI agents navigate the full innovation lifecycle — from
              market insights to launch — with automated security governance.
            </p>
          </motion.div>

          {/* Diamond preview */}
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="w-full max-w-3xl mx-auto mb-10 px-4"
          >
            <DiamondVisualization phaseStatuses={{}} currentPhase="" />
          </motion.div>

          {/* Feature pills */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.4 }}
            className="flex flex-wrap justify-center gap-2 mb-10"
          >
            {[
              { icon: "🔭", label: "6 Explorer Agents" },
              { icon: "🎯", label: "5 Definer Agents" },
              { icon: "⚡", label: "5 Creator Agents" },
              { icon: "🚀", label: "5 Launch Agents" },
              { icon: "🛡️", label: "Security Agent" },
              { icon: "🧠", label: "AWS Bedrock" },
              { icon: "📊", label: "Datadog LLMObs" },
              { icon: "⚙️", label: "LangGraph" },
            ].map((f) => (
              <span key={f.label}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-full border border-white/8 bg-white/3 text-xs text-slate-400">
                <span>{f.icon}</span>
                {f.label}
              </span>
            ))}
          </motion.div>

          {/* Form card */}
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            className="w-full max-w-2xl mx-auto"
          >
            <div className="glass rounded-2xl p-6 shadow-card">
              <h2 className="text-lg font-semibold text-white mb-5 text-center">
                Start Your Innovation Journey
              </h2>
              <SessionForm onCreated={handleCreated} />
            </div>
          </motion.div>
        </main>

        {/* Footer */}
        <footer className="border-t border-white/5 py-4 px-6 text-center text-xs text-slate-600">
          Powered by LangGraph · AWS Bedrock Claude · Datadog LLM Observability
        </footer>
      </div>
    </div>
  );
}
