"use client";

import { useEffect, useRef, useState } from "react";
import { openEventStream } from "@/lib/api";
import type { AgentStatus, PipelineEvent, PhaseStatus, SecurityCheck } from "@/types";

interface AgentState {
  status: AgentStatus;
  output: string;
  preview: string;
}

interface SessionLiveState {
  currentPhase: string;
  phaseStatuses: Record<string, PhaseStatus>;
  agentStates: Record<string, AgentState>;
  securityCheck1: Partial<SecurityCheck> | null;
  securityCheck2: Partial<SecurityCheck> | null;
  events: PipelineEvent[];
  isComplete: boolean;
  isConnected: boolean;
  error: string | null;
}

export function useSessionStream(sessionId: string | null): SessionLiveState {
  const [state, setState] = useState<SessionLiveState>({
    currentPhase: "explorer",
    phaseStatuses: {},
    agentStates: {},
    securityCheck1: null,
    securityCheck2: null,
    events: [],
    isComplete: false,
    isConnected: false,
    error: null,
  });

  const esRef = useRef<EventSource | null>(null);

  useEffect(() => {
    if (!sessionId) return;

    const es = openEventStream(sessionId);
    esRef.current = es;

    es.onopen = () => {
      setState((s) => ({ ...s, isConnected: true }));
    };

    es.onmessage = (ev) => {
      try {
        const event: PipelineEvent = JSON.parse(ev.data);
        handleEvent(event);
      } catch {
        // ignore parse errors
      }
    };

    es.onerror = () => {
      setState((s) => ({ ...s, isConnected: false, error: "Stream disconnected" }));
      es.close();
    };

    return () => {
      es.close();
      esRef.current = null;
    };
  }, [sessionId]);

  function handleEvent(event: PipelineEvent) {
    setState((prev) => {
      const next = { ...prev, events: [...prev.events, event] };

      switch (event.type) {
        case "snapshot": {
          const data = event.data as { phase_statuses?: Record<string, PhaseStatus> };
          next.currentPhase = event.phase;
          next.phaseStatuses = data.phase_statuses ?? prev.phaseStatuses;
          next.isConnected = true;
          break;
        }
        case "phase_start": {
          next.currentPhase = event.phase;
          next.phaseStatuses = {
            ...prev.phaseStatuses,
            [event.phase]: "running",
          };
          break;
        }
        case "agent_start": {
          if (event.agent) {
            next.agentStates = {
              ...prev.agentStates,
              [event.agent]: { status: "running", output: "", preview: "" },
            };
          }
          break;
        }
        case "agent_done": {
          if (event.agent) {
            next.agentStates = {
              ...prev.agentStates,
              [event.agent]: {
                status: "done",
                output: event.message,
                preview: event.message.slice(0, 300),
              },
            };
          }
          break;
        }
        case "security_check": {
          const data = event.data as {
            risk_score?: number;
            blockers?: string[];
          };
          const checkData: Partial<SecurityCheck> = {
            decision: event.status as SecurityCheck["decision"],
            risk_score: data.risk_score,
            summary: event.message,
            blockers: data.blockers ?? [],
          };
          if (event.phase === "security_1") {
            next.securityCheck1 = checkData;
          } else {
            next.securityCheck2 = checkData;
          }
          next.phaseStatuses = {
            ...prev.phaseStatuses,
            [event.phase]: event.status as PhaseStatus,
          };
          break;
        }
        case "pipeline_complete": {
          next.isComplete = true;
          next.currentPhase = "done";
          break;
        }
        case "stream_end": {
          next.isComplete = true;
          next.isConnected = false;
          break;
        }
        case "error": {
          next.error = event.message;
          break;
        }
      }

      return next;
    });
  }

  return state;
}
