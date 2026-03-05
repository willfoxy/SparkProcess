import type { Config } from "tailwindcss";

export default {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        bg: {
          deep:   "#050816",
          base:   "#080d1a",
          surface: "#0d1629",
          glass:  "rgba(255,255,255,0.04)",
        },
        explorer: {
          DEFAULT: "#3B82F6",
          glow:   "rgba(59,130,246,0.35)",
          muted:  "rgba(59,130,246,0.15)",
        },
        definer: {
          DEFAULT: "#8B5CF6",
          glow:   "rgba(139,92,246,0.35)",
          muted:  "rgba(139,92,246,0.15)",
        },
        creator: {
          DEFAULT: "#EC4899",
          glow:   "rgba(236,72,153,0.35)",
          muted:  "rgba(236,72,153,0.15)",
        },
        launch: {
          DEFAULT: "#10B981",
          glow:   "rgba(16,185,129,0.35)",
          muted:  "rgba(16,185,129,0.15)",
        },
        security: {
          DEFAULT: "#F59E0B",
          glow:   "rgba(245,158,11,0.35)",
          muted:  "rgba(245,158,11,0.15)",
        },
        approved:  "#10B981",
        flagged:   "#F59E0B",
        rejected:  "#EF4444",
      },
      fontFamily: {
        sans:  ["Inter var", "Inter", "system-ui", "sans-serif"],
        mono:  ["JetBrains Mono", "Fira Code", "monospace"],
        display: ["Inter var", "system-ui", "sans-serif"],
      },
      backgroundImage: {
        "grid-subtle": "linear-gradient(rgba(59,130,246,0.03) 1px,transparent 1px),linear-gradient(90deg,rgba(59,130,246,0.03) 1px,transparent 1px)",
        "gradient-radial-blue": "radial-gradient(ellipse at top left, rgba(59,130,246,0.15), transparent 50%)",
        "gradient-radial-purple": "radial-gradient(ellipse at top right, rgba(139,92,246,0.1), transparent 50%)",
      },
      backgroundSize: {
        "grid": "48px 48px",
      },
      animation: {
        "pulse-slow": "pulse 3s cubic-bezier(0.4,0,0.6,1) infinite",
        "glow": "glow 2s ease-in-out infinite alternate",
        "slide-up": "slideUp 0.5s cubic-bezier(0.16,1,0.3,1)",
        "fade-in": "fadeIn 0.3s ease",
        "flow": "flow 3s linear infinite",
        "shimmer": "shimmer 2s linear infinite",
      },
      keyframes: {
        glow: {
          "0%":   { boxShadow: "0 0 5px currentColor" },
          "100%": { boxShadow: "0 0 20px currentColor, 0 0 40px currentColor" },
        },
        slideUp: {
          "0%":   { opacity: "0", transform: "translateY(16px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        fadeIn: {
          "0%":   { opacity: "0" },
          "100%": { opacity: "1" },
        },
        flow: {
          "0%":   { strokeDashoffset: "200" },
          "100%": { strokeDashoffset: "0" },
        },
        shimmer: {
          "0%":   { backgroundPosition: "-200% 0" },
          "100%": { backgroundPosition: "200% 0" },
        },
      },
      boxShadow: {
        "glass":      "0 4px 24px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.06)",
        "glow-blue":  "0 0 24px rgba(59,130,246,0.3), 0 0 48px rgba(59,130,246,0.1)",
        "glow-purple":"0 0 24px rgba(139,92,246,0.3), 0 0 48px rgba(139,92,246,0.1)",
        "glow-pink":  "0 0 24px rgba(236,72,153,0.3), 0 0 48px rgba(236,72,153,0.1)",
        "glow-green": "0 0 24px rgba(16,185,129,0.3), 0 0 48px rgba(16,185,129,0.1)",
        "glow-amber": "0 0 24px rgba(245,158,11,0.3), 0 0 48px rgba(245,158,11,0.1)",
        "card":       "0 8px 32px rgba(0,0,0,0.6), 0 1px 0 rgba(255,255,255,0.05)",
      },
    },
  },
  plugins: [],
} satisfies Config;
