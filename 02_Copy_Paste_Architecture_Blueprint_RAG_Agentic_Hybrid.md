# Squad 1 Copy-Paste Architecture Blueprint

Purpose: give your team a rapid technical starting point for any challenge.

Challenge selected for Squad 1: AI Consultant Selection Assistant

Target outcome for this challenge:
- rank best-fit consultants quickly
- provide explainable and auditable rationale
- flag skill gaps early
- keep a human decision-maker in control
- reduce manual review effort for sales/staffing managers
- support unbiased, data-driven shortlisting

Use this file in two ways:
- Pick one architecture template after challenge reveal.
- Copy the sample contracts and pseudocode into your codebase.

For your challenge, recommended default is Hybrid.

## 1) Architecture Choice Guide

Choose RAG-first if:
- Challenge depends on policy, SOP, playbook, knowledge base, or internal docs.
- Trust, citations, and reduced hallucination are important.

Choose Agentic-first if:
- Challenge needs decisions across multiple steps.
- The solution must route tasks, call tools, or automate actions.

Choose Hybrid if:
- You need both knowledge grounding and multi-step action orchestration.

Decision rule:
- If unknown, start Hybrid-lite:
  - first implement retrieval + answer generation,
  - then add one orchestration step.

Decision for Squad 1:
- Use Hybrid now: orchestration for ranking workflow plus RAG grounding for explainability.

## 2) Shared Logical Components (for all patterns)

- Client UI
  - input form
  - results panel
  - sources or reasoning panel

- Orchestrator API
  - receives request
  - validates input
  - calls retrieval and/or model
  - returns structured output

- AI Adapter
  - abstract model invocation behind one interface
  - allows mock provider now and Foundry provider later

- Data Adapter
  - loads local sample data first
  - can swap to cloud/vector source later

- Integration Adapters
  - consultant tracker adapter (future live sync)
  - resume database adapter (future parsing/enrichment)
  - Power BI export adapter (immediate MVP-friendly source)

- Logging
  - request id, input summary, selected context, output summary, latency

- Guardrails
  - deterministic scoring envelope
  - explanation completeness checks
  - low-confidence trigger for human review

## 2.1) Challenge-Specific Data Model

### Consultant profile schema
```json
{
  "consultantId": "C-001",
  "name": "string",
  "primarySkills": ["azure", "python", "devops"],
  "secondarySkills": ["sql", "powerbi"],
  "experienceYears": 5,
  "location": "Toronto",
  "timezone": "EST",
  "availabilityDate": "2026-08-20",
  "certifications": ["AZ-104", "AZ-900"],
  "behavioralSignals": {
    "collaboration": 0.0,
    "communication": 0.0,
    "adaptability": 0.0
  },
  "degree": "BSc Computer Science",
  "projectTags": ["cloud-migration", "itops"],
  "domainExperience": ["retail", "banking"]
}
```

### Role request schema
```json
{
  "requestId": "R-101",
  "title": "Cloud Support Engineer",
  "mustHaveSkills": ["azure", "incident-management"],
  "niceToHaveSkills": ["python", "automation"],
  "requiredCertifications": ["AZ-104"],
  "behavioralPreferences": ["communication", "adaptability"],
  "minExperienceYears": 3,
  "locationConstraint": "North America",
  "timezoneConstraint": "EST/CST",
  "startDate": "2026-09-01",
  "industry": "financial-services"
}
```

## 3) API Contracts (copy/paste)

### Request Contract
```json
{
  "userId": "string",
  "scenario": "consultant-selection",
  "input": {
    "text": "role request and context",
    "metadata": {
      "channel": "staffing",
      "priority": "low|medium|high"
    }
  },
  "options": {
    "mode": "rag|agentic|hybrid",
    "maxTokens": 800,
    "temperature": 0.2
  }
}
```

### Response Contract
```json
{
  "requestId": "string",
  "summary": "string",
  "recommendations": ["string"],
  "confidence": 0.0,
  "candidateRankings": [
    {
      "consultantId": "string",
      "name": "string",
      "fitScore": 0,
      "matchedSkills": ["string"],
      "matchedCertifications": ["string"],
      "behavioralFit": "high|medium|low",
      "gaps": ["string"],
      "rationale": "string",
      "riskFlags": ["string"]
    }
  ],
  "sources": [
    {
      "title": "string",
      "snippet": "string",
      "score": 0.0
    }
  ],
  "assumptions": ["string"],
  "limitations": ["string"],
  "latencyMs": 0
}
```

## 4) RAG-First Blueprint

### Flow
1. Receive user question or case.
2. Retrieve top-k consultant profiles and matching policy/context documents.
3. Build grounded prompt with retrieved context and explicit scoring rubric.
4. Generate answer with source references.
5. Return shortlist recommendations and citations.

### Prompt Template
```text
System:
You are an enterprise assistant. Use only the provided context.
If context is insufficient, say "Insufficient evidence" and ask for missing data.
Output JSON matching the schema exactly.

Context:
{{retrieved_chunks}}

User request:
{{user_input}}

Required JSON fields:
summary, candidateRankings, confidence, assumptions, limitations
```

### Pseudocode
```text
function handleRag(request):
  docs = retrieveTopK(request.input.text, k=5)
  prompt = buildGroundedPrompt(docs, request.input.text)
  modelOut = aiAdapter.generate(prompt)
  return shapeResponse(modelOut, docs)
```

## 5) Agentic-First Blueprint

### Flow
1. Parse role request and normalize requirement fields.
2. Run candidate retrieval and hard-constraint filtering.
3. Run scoring and rank candidates.
4. Generate explanation and gap analysis per top candidate.
5. Flag low-confidence or high-risk recommendations for human review.

### Agent Step Schema
```json
{
  "step": 1,
  "goal": "Normalize role constraints",
  "tool": "role_parser",
  "input": "role request",
  "output": "structured constraints",
  "status": "done"
}
```

### Pseudocode
```text
function handleAgentic(request):
  intent = classifyIntent(request.input.text)
  plan = createPlan(intent)
  stepResults = []
  for step in plan:
    stepResults.append(runTool(step))
  final = synthesizeDecision(stepResults)
  return shapeResponse(final, sources=[])
```

## 6) Hybrid Blueprint (Recommended Default)

### Flow
1. Agent parses role request into structured constraints.
2. Retrieval pulls top consultant profiles and relevant context docs.
3. Scoring step computes candidate fit (skills, certifications, behavior, experience, constraints).
4. LLM produces explainable rationale and skill gap notes.
5. Return ranked shortlist, confidence, citations, and human review flags.

### Scoring logic (deterministic)
Use a deterministic score before final LLM explanation to reduce subjectivity.

$$
FitScore = 0.35S_{must} + 0.15S_{nice} + 0.15S_{cert} + 0.10S_{behavior} + 0.15S_{exp} + 0.10S_{constraint}
$$

Where:
- $S_{must}$: must-have skill coverage
- $S_{nice}$: nice-to-have skill coverage
- $S_{cert}$: required certification alignment
- $S_{behavior}$: behavioral signal alignment to role preferences
- $S_{exp}$: experience alignment
- $S_{constraint}$: location/time/availability fit

Practical guardrail:
- if $S_{must} < 0.6$, candidate cannot rank in top 3 unless explicit override is explained.
- if confidence < threshold, system must return "human review required" flag.

### Pseudocode
```text
function handleHybrid(request):
  role = parseRoleRequest(request.input.text)
  candidates = retrieveCandidates(role, k=25)
  filtered = applyHardConstraints(candidates, role)
  scored = deterministicRank(filtered, role)
  top = takeTop(scored, 5)
  evidence = retrieveContextDocs(role)
  rationale = generateExplanations(top, role, evidence)
  return shapeResponse(rationale, evidence)
```

## 6.1) Integration Plan: Power BI + Trackers + Resume Data

Phase 1 (Hackathon MVP):
- consume a clean export aligned with existing Power BI consultant dimensions
- map columns to canonical consultant profile schema

Phase 2 (Post-hackathon):
- add consultant tracker API connector for near real-time profile updates
- add resume parsing/enrichment pipeline

Phase 3 (Enterprise hardening):
- data quality rules, lineage, and refresh monitoring
- governance dashboards for recommendation quality and fairness

## 7) Foundry-Day Integration Plan

Because Foundry access may only arrive on hackathon day:

Before access:
- implement aiAdapter with mock responses
- implement full UI and orchestration flow
- validate with synthetic dataset (10-20 records)

After access:
- add foundryAdapter implementation
- swap adapter selection via env variable
- rerun smoke tests

Foundry note:
- keep deterministic ranking in code, use model for explanation and summarization.
- keep the final staffing decision outside the model output path.

Environment toggle example:
```text
AI_PROVIDER=mock
AI_PROVIDER=foundry
```

## 8) Minimal Data Strategy

Use one file now for fast testing:
- sample_cases.jsonl

For this challenge, create at least:
- consultants.jsonl (20-50 synthetic profiles)
- role_requests.jsonl (8-12 role requests)
- policies.jsonl (optional brief policy snippets for explanation style and compliance wording)

Fields:
- consultantId / requestId
- normalized skills arrays
- experience and constraint fields
- expected_top_candidates
- certifications and behavioral signals

If no real data is available:
- create synthetic records and clearly label assumptions.

## 9) MVP Acceptance Criteria

Your prototype is demo-ready only if all are true:
- One happy path runs from input to output without manual fixing.
- Output includes actionable recommendation.
- Output includes confidence or rationale signal.
- If using RAG/Hybrid, at least one source citation is shown.
- Response time is stable enough for live demo.
- Top 5 ranking includes matched skills and explicit gaps per candidate.
- Human override path is visible (keep humans in charge).

## 10) Non-Goals (to avoid overbuild)

Do not build unless challenge explicitly needs it:
- production-grade auth
- full CI/CD pipeline
- complex infra automation
- multi-agent architecture
- large-scale data ingestion
- automatic hiring decision without human review

## 11) Demo Reliability Checklist

- [ ] app starts in one command
- [ ] sample input prepared
- [ ] expected output screenshot captured
- [ ] fallback recording prepared
- [ ] presenter machine validated
- [ ] backup presenter briefed

## 12) One-Slide Architecture Description (for judges)

"Our AI Consultant Selection Assistant uses a hybrid architecture: deterministic ranking for consistency, retrieval grounding for evidence, and LLM-generated explanations for transparency. This provides fast shortlist generation, auditable rationale, early skill-gap detection, and explicit human-in-the-loop control."

## 13) Recommended MVP Screens

1. Role Intake screen
- fields for must-have skills, preferred skills, constraints, and start date

2. Ranked Shortlist screen
- top candidates, fit score, matched skills, and flagged gaps

3. Explainability panel
- evidence snippets, rationale, confidence, and review warnings

## 14) Bias and Governance Notes (for judges)

Keep these principles explicit in your demo:
- score primarily on role-relevant capability signals
- avoid protected attributes in ranking logic
- log rationale for each recommendation
- require human approval before any final staffing decision

## 15) US Perspective Guardrails (Practical)

- Label output as "recommendation" and "decision support" in UI copy.
- Show feature inputs used for scoring and explanation.
- Provide reason codes for top-ranked and lower-ranked candidates.
- Maintain an audit trail for input, scoring components, and output rationale.
- Include manual override and reviewer acknowledgment step.
