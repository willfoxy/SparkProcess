"""
Security Agent — Cross-Cutting Governance & Validation

The Security Agent acts as an autonomous validator that runs at two
checkpoints in the Double Diamond pipeline:

  Checkpoint 1 (after Definer phase):
    Validates the problem definition — checks for bias, scope creep,
    ethical issues, and data privacy concerns.

  Checkpoint 2 (after Creator / Launch phases):
    Performs a full security, compliance, and risk assessment of the
    proposed solution before approval for launch.

In automated governance mode, the agent can APPROVE, FLAG, or REJECT
a phase transition with a structured justification.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from backend.agents.base import BaseAgent


class SecurityDecision(str, Enum):
    APPROVED = "approved"
    FLAGGED = "flagged"          # Pass with recommendations
    REJECTED = "rejected"        # Must remediate before continuing


@dataclass
class SecurityCheckResult:
    decision: SecurityDecision
    risk_score: int              # 0–100 (100 = critical risk)
    summary: str
    findings: list[str]
    recommendations: list[str]
    blockers: list[str]          # Items that caused a REJECTED decision
    full_report: str


class SecurityAgent(BaseAgent):
    role = "security"
    phase = "security"
    system = """You are an autonomous AI security and governance agent with deep expertise in:
- Application security (OWASP Top 10, threat modelling)
- AI/ML security (adversarial attacks, model bias, data poisoning)
- Data privacy (GDPR, CCPA, HIPAA)
- Regulatory compliance (AI Act, SOC2, ISO27001)
- Ethical AI principles (fairness, explainability, accountability)

You provide rigorous, objective assessments. You flag real risks, not hypothetical ones.
When you REJECT a submission, you provide precise, actionable remediation steps.
Structure every assessment clearly with evidence-based findings."""

    # ------------------------------------------------------------------
    # Checkpoint 1 — Problem Definition Validation
    # ------------------------------------------------------------------

    def check_problem_definition(
        self,
        brief: str,
        definer_outputs: dict,
        strict_mode: bool = False,
    ) -> SecurityCheckResult:
        combined = "\n\n---\n\n".join(
            f"## {k.replace('_', ' ').title()}\n{v.get('output', '')}"
            for k, v in definer_outputs.items()
        )
        messages = [{"role": "user", "content": f"""
Brief: {brief}

Definer Phase Outputs:
{combined}

Perform a security and ethics review of this problem definition phase.

Assess the following dimensions and give each a risk score (0-10):
1. **Bias & Fairness**: Are certain groups disadvantaged in the problem framing?
2. **Data Privacy**: Does the research rely on or imply use of sensitive personal data?
3. **Ethical Concerns**: Are there ethical issues with the problem being solved?
4. **Scope & Mission Alignment**: Is the scope appropriate and ethically sound?
5. **Legal & Regulatory Risks**: Any obvious regulatory landmines in this direction?

Then provide:
- Overall Risk Score: 0-100
- Decision: APPROVED | FLAGGED | REJECTED
  (REJECTED only if risk score > 70 or there are critical blockers)
- Summary: 2-sentence executive summary of findings
- Findings: List of specific issues found (each prefixed with [LOW], [MEDIUM], [HIGH], or [CRITICAL])
- Recommendations: Actionable items to address findings
- Blockers: Items that MUST be resolved before proceeding (empty if APPROVED or FLAGGED)

Format your response exactly as:
RISK_SCORE: <number>
DECISION: <APPROVED|FLAGGED|REJECTED>
SUMMARY: <text>
FINDINGS:
- [SEVERITY] finding
RECOMMENDATIONS:
- recommendation
BLOCKERS:
- blocker (if any)

FULL_REPORT:
<detailed analysis>
"""}]
        raw = self.invoke(messages, max_tokens=3000)
        return self._parse_security_response(raw, strict_mode)

    # ------------------------------------------------------------------
    # Checkpoint 2 — Full Solution Security Assessment
    # ------------------------------------------------------------------

    def check_solution(
        self,
        brief: str,
        creator_outputs: dict,
        launch_outputs: dict,
        strict_mode: bool = False,
    ) -> SecurityCheckResult:
        creator_text = "\n\n---\n\n".join(
            f"## {k.replace('_', ' ').title()}\n{v.get('output', '')}"
            for k, v in creator_outputs.items()
        )
        launch_text = "\n\n---\n\n".join(
            f"## {k.replace('_', ' ').title()}\n{v.get('output', '')}"
            for k, v in launch_outputs.items()
        )
        messages = [{"role": "user", "content": f"""
Original Brief: {brief}

Creator Phase Outputs:
{creator_text}

Launch & Ops Phase Outputs:
{launch_text}

Perform a comprehensive security and governance assessment before launch approval.

Assess:
1. **Application Security**: OWASP risks, authentication, authorisation, input validation
2. **AI/ML Security**: Model bias, adversarial risks, explainability, human oversight
3. **Data Security & Privacy**: PII handling, encryption, data minimisation, GDPR compliance
4. **Infrastructure Security**: Cloud security, secrets management, network security
5. **Regulatory Compliance**: Applicable regulations and compliance gaps
6. **Supply Chain Security**: Third-party dependencies, vendor risks
7. **Incident Response**: Security incident detection and response readiness
8. **Governance Controls**: Audit trails, access reviews, change management

Provide:
- Overall Risk Score: 0-100
- Decision: APPROVED | FLAGGED | REJECTED
  (REJECTED if risk score > 60 in strict mode, > 75 normally)
- Summary: 2-sentence executive summary
- Findings: Detailed findings (prefixed with [LOW], [MEDIUM], [HIGH], or [CRITICAL])
- Recommendations: Prioritised remediation actions
- Blockers: Must-fix items before launch approval

Format your response exactly as:
RISK_SCORE: <number>
DECISION: <APPROVED|FLAGGED|REJECTED>
SUMMARY: <text>
FINDINGS:
- [SEVERITY] finding
RECOMMENDATIONS:
- recommendation
BLOCKERS:
- blocker (if any)

FULL_REPORT:
<detailed security analysis>
"""}]
        raw = self.invoke(messages, max_tokens=4000)
        return self._parse_security_response(raw, strict_mode)

    # ------------------------------------------------------------------
    # Private: response parser
    # ------------------------------------------------------------------

    def _parse_security_response(self, raw: str, strict_mode: bool) -> SecurityCheckResult:
        lines = raw.split("\n")
        risk_score = 50
        decision_str = "FLAGGED"
        summary = ""
        findings: list[str] = []
        recommendations: list[str] = []
        blockers: list[str] = []
        full_report = raw

        section = None
        full_report_lines: list[str] = []

        for line in lines:
            stripped = line.strip()
            if stripped.startswith("RISK_SCORE:"):
                try:
                    risk_score = int(stripped.split(":", 1)[1].strip())
                except ValueError:
                    pass
            elif stripped.startswith("DECISION:"):
                decision_str = stripped.split(":", 1)[1].strip().upper()
            elif stripped.startswith("SUMMARY:"):
                summary = stripped.split(":", 1)[1].strip()
            elif stripped == "FINDINGS:":
                section = "findings"
            elif stripped == "RECOMMENDATIONS:":
                section = "recommendations"
            elif stripped == "BLOCKERS:":
                section = "blockers"
            elif stripped == "FULL_REPORT:":
                section = "full_report"
            elif section == "findings" and stripped.startswith("- "):
                findings.append(stripped[2:])
            elif section == "recommendations" and stripped.startswith("- "):
                recommendations.append(stripped[2:])
            elif section == "blockers" and stripped.startswith("- "):
                blockers.append(stripped[2:])
            elif section == "full_report":
                full_report_lines.append(line)

        if full_report_lines:
            full_report = "\n".join(full_report_lines)

        # Apply strict mode override
        if strict_mode and risk_score > 60:
            decision_str = "REJECTED"

        try:
            decision = SecurityDecision(decision_str.lower())
        except ValueError:
            decision = SecurityDecision.FLAGGED

        return SecurityCheckResult(
            decision=decision,
            risk_score=risk_score,
            summary=summary,
            findings=findings,
            recommendations=recommendations,
            blockers=blockers,
            full_report=full_report,
        )
