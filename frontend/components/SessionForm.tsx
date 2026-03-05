"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { createSession } from "@/lib/api";

interface Props {
  onCreated: (sessionId: string) => void;
}

const EXAMPLES = [
  "How might we reduce food waste in urban restaurants using AI and IoT sensors?",
  "Design a mental health platform for remote workers that builds lasting habits.",
  "Create a peer-to-peer renewable energy trading marketplace for communities.",
  "Build an AI co-pilot for small business owners that automates financial decisions.",
];

export default function SessionForm({ onCreated }: Props) {
  const [brief, setBrief] = useState("");
  const [org, setOrg] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!brief.trim() || loading) return;
    setLoading(true);
    setError(null);
    try {
      const session = await createSession(brief.trim(), org.trim());
      onCreated(session.session_id);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to start session");
      setLoading(false);
    }
  }

  return (
    <div className="w-full max-w-2xl mx-auto">
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Brief textarea */}
        <div>
          <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
            Innovation Brief *
          </label>
          <textarea
            value={brief}
            onChange={(e) => setBrief(e.target.value)}
            placeholder="Describe your innovation challenge or opportunity…"
            rows={4}
            className="
              w-full rounded-xl px-4 py-3 text-sm text-white placeholder-slate-600
              bg-white/4 border border-white/10 resize-none
              focus:outline-none focus:border-blue-500/50 focus:ring-1 focus:ring-blue-500/30
              transition-all duration-200
            "
          />
          {/* Example chips */}
          <div className="mt-2 flex flex-wrap gap-1.5">
            {EXAMPLES.map((ex, i) => (
              <button
                key={i}
                type="button"
                onClick={() => setBrief(ex)}
                className="
                  text-xs px-2.5 py-1 rounded-full border border-white/10 text-slate-500
                  hover:border-blue-500/40 hover:text-blue-400 hover:bg-blue-500/8
                  transition-all duration-150
                "
              >
                Example {i + 1}
              </button>
            ))}
          </div>
        </div>

        {/* Organisation (optional) */}
        <div>
          <label className="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
            Organisation <span className="text-slate-600 normal-case font-normal">(optional)</span>
          </label>
          <input
            value={org}
            onChange={(e) => setOrg(e.target.value)}
            placeholder="e.g. Acme Corp"
            className="
              w-full rounded-xl px-4 py-2.5 text-sm text-white placeholder-slate-600
              bg-white/4 border border-white/10
              focus:outline-none focus:border-blue-500/50 focus:ring-1 focus:ring-blue-500/30
              transition-all duration-200
            "
          />
        </div>

        {error && (
          <p className="text-sm text-red-400 bg-red-500/10 border border-red-500/20 rounded-lg px-3 py-2">
            {error}
          </p>
        )}

        {/* Submit */}
        <motion.button
          type="submit"
          disabled={!brief.trim() || loading}
          whileHover={{ scale: brief.trim() && !loading ? 1.02 : 1 }}
          whileTap={{ scale: brief.trim() && !loading ? 0.98 : 1 }}
          className="
            w-full py-3 rounded-xl font-semibold text-sm text-white
            bg-gradient-to-r from-blue-600 to-purple-600
            hover:from-blue-500 hover:to-purple-500
            disabled:opacity-40 disabled:cursor-not-allowed
            transition-all duration-200 shadow-lg shadow-blue-600/20
            relative overflow-hidden
          "
        >
          {loading ? (
            <span className="flex items-center justify-center gap-2">
              <svg className="animate-spin w-4 h-4" viewBox="0 0 24 24" fill="none">
                <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="3" opacity="0.3" />
                <path d="M12 2a10 10 0 0 1 10 10" stroke="currentColor" strokeWidth="3" strokeLinecap="round" />
              </svg>
              Starting pipeline…
            </span>
          ) : (
            <span className="flex items-center justify-center gap-2">
              <span>Launch Double Diamond</span>
              <span>→</span>
            </span>
          )}
        </motion.button>
      </form>
    </div>
  );
}
