# Squad 1 Challenge-Day 45-Minute Decision Worksheet

Challenge focus: AI Consultant Selection Assistant

Purpose: make a fast, high-quality challenge decision and lock an MVP without wasting build time.

Challenge brief summary:
- Current consultant selection is slow, subjective, and not fully grounded in available skills data.
- Expected MVP should rank best-fit consultants in seconds, provide explainable rationale, reduce bias, and flag skill gaps early.
- PO emphasis: include skills, certifications, behavioral assessment signals, and role requirements in ranking logic.
- Existing Power BI dashboards already contain consultant overview data (background, experience, location, degree) and should be leveraged.
- US perspective: design for AI-assisted recommendation, not fully automated final decisioning.

How to use:
- Fill this worksheet live in your squad call between challenge reveal and coding start.
- Timebox each section strictly.
- If a field is unknown, write an assumption and continue.

## Team Setup (Minute 0-3)
- Date: 2026-08-12
- Challenge selected: AI Consultant Selection Assistant
- Product Owner: Vince Mnich
- SME/Coach: Mayank Arora
- Facilitator (timekeeper): Alhassan Diallo
- Notes owner: David Luo

## Section A: Problem Framing (Minute 3-15)
Answer these seven questions. Do not move forward until all seven are filled.

1. Primary user
- Who is the user for this prototype?
- Answer: Regional staffing manager / account manager selecting consultants for a role.

2. Core pain point
- What is the single highest-value pain point?
- Answer: Matching consultants to demand is manual, inconsistent, and too slow for business timelines.

3. Trigger moment
- When does this problem occur in the workflow?
- Answer: Immediately after a client role request is opened and before shortlist submission.

4. Required input
- What information does the user provide?
- Answer: Role requirements, must-have skills, preferred skills, certifications, behavioral assessment signals, location/time-zone, seniority, start date, and optional client context.

5. Required output
- What decision, recommendation, or artifact must be produced?
- Answer: Ranked shortlist of consultants with fit score, explainable rationale, and flagged skill gaps.

6. Data source
- What data/docs are available today for demo?
- Answer: Synthetic consultant profiles + role requirement dataset + exported fields aligned with existing Power BI consultant views + optional policy notes for explanation style.

7. Success metric
- What one measurable outcome proves value?
- Answer: Reduce shortlist preparation time from approximately 30 minutes to less than 5 minutes while preserving explanation quality and traceability.

Definition check:
- We can state the problem in one sentence: Yes
- We can show value in one metric: Yes

## Section B: Architecture Decision (Minute 15-23)
Choose one pattern only.

### Option 1: RAG-first
Use when answer quality depends on enterprise documents or knowledge.
- Fits this challenge? Partially
- Why: Good for grounding explanations and policy constraints, but not enough for ranking workflow alone.

### Option 2: Agentic-first
Use when workflow needs multi-step planning, tool calls, or routing.
- Fits this challenge? Partially
- Why: Good for orchestration, but needs grounded retrieval to keep recommendations auditable.

### Option 3: Hybrid (Agent + RAG)
Use when both retrieval grounding and workflow actions are required.
- Fits this challenge? Yes
- Why: This challenge needs explainable ranking decisions plus grounded evidence from skills profiles and role requirements.

Decision:
- Selected architecture: Hybrid
- Reason in one sentence: Hybrid provides fast ranking orchestration and auditable evidence-based reasoning in one flow.

## Section C: Scope Lock (Minute 23-30)
Lock an MVP that is demonstrable by lunch.

- One target persona: Staffing manager in North America region
- One core workflow: Submit role requirements -> receive ranked consultant shortlist with rationale, skill-gap flags, and review warning if confidence is low
- One happy-path demo scenario: Cloud support engineer request returns top 5 candidates with fit explanation and suggested upskilling notes
- Three outputs max:
  - Output 1: Ranked top candidates with fit score
  - Output 2: Explanation per candidate (matched skills, certifications, behavioral/experience alignment, constraints)
  - Output 3: Skill gap and risk flags (for transparent decisions)
- One differentiator (optional): Fairness guardrail check with reasons when confidence is low

Out of scope list (mandatory):
- Production identity and RBAC integration
- Full ATS/HRIS integrations
- Advanced learning loop and continuous retraining

In-scope integration for MVP:
- Read from exported consultant profile data aligned with Power BI dimensions
- Show a clear adapter pattern for future integration with consultant trackers and resume databases

## Section D: Build Plan (Minute 30-38)
Assign owners and deadlines.

- UI owner: Lucas Michalski
- Backend/API owner: Maheep Chawla
- AI prompt/retrieval owner: Lucas Michalski
- Data prep owner: David Luo
- Demo script owner: David Luo
- Presentation deck owner: David Luo
- Integration/stability owner (DevOps): Alhassan Diallo

Milestones:
- M1 (first runnable end-to-end): 11:45 AM
- M2 (value outputs validated): 2:15 PM
- M3 (presentation-ready freeze): 3:20 PM

## Section E: Risk and Fallback (Minute 38-43)
Top risks (rank highest first):
1. Data quality mismatch between role requirements and consultant profiles
2. Ranking output appears subjective if rationale is weak
3. Demo instability from late integration changes
4. Compliance and fairness concerns in US AI-assisted staffing decisions

Mitigation actions:
- Risk 1 action: Normalize profile and role schema, validate 10 sample cases early
- Risk 2 action: Force structured explanation fields and include evidence snippets
- Risk 3 action: Feature freeze at 3:20 PM and maintain screenshot/video fallback
- Risk 4 action: Explicitly state human-in-the-loop final decision, log rationale, and avoid protected-attribute based ranking

Demo fallback assets checklist:
- [ ] Screenshots for each demo step
- [ ] 60-90 second backup video
- [ ] One local test dataset
- [ ] Backup presenter available

## Section F: Go/No-Go Gate (Minute 43-45)
Proceed only if all are Yes.
- [ ] Problem statement is clear and specific
- [ ] MVP scope is realistic for same-day delivery
- [ ] Architecture choice is aligned to challenge
- [ ] Roles and owners are assigned
- [ ] First milestone time is agreed

Final call:
- GO / NO-GO
- If NO-GO, what is being reduced immediately?
  ______________________________________

---

## Baseline KPI Targets For Judging Narrative

| KPI | Current process (estimate) | MVP target |
|---|---:|---:|
| Time to first shortlist | 30 min | <= 5 min |
| Evidence-backed recommendation coverage | < 20% | >= 90% |
| Explainability per candidate | low/inconsistent | structured per candidate |
| Early skill gap detection | ad hoc | automated flag in each run |
| Recommendation traceability | limited | rationale stored for each top candidate |

---

## US AI-Assisted Decision Guardrails (MVP)

- Position the tool as decision support, not autonomous hiring/staffing decision-maker.
- Include a visible "human review required" step before final selection.
- Exclude protected characteristics from scoring features.
- Preserve rationale logs for auditability and post-hoc review.
- Add a confidence threshold and escalation path for borderline recommendations.

---

## Fast Scoring Matrix (Optional)
Score each idea from 1 (low) to 5 (high).

| Criteria | Idea A | Idea B | Idea C |
|---|---:|---:|---:|
| Business value |  |  |  |
| Feasibility in one day |  |  |  |
| Data availability |  |  |  |
| AI fit |  |  |  |
| Demo clarity |  |  |  |
| Team skill match |  |  |  |
| Differentiation |  |  |  |
| Total |  |  |  |

Rule: do not pick any idea scoring below 3 in feasibility.