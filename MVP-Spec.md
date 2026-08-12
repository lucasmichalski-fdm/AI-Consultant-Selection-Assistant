# Starter Spec: Consultant Comparison and Ranking

## 1. Purpose

Define a minimal, auditable process to compare consultant profiles and resume content against a provided job description or role posting, then return a ranked list of best-fit consultants.

This starter spec intentionally covers only:
- candidate-to-role comparison
- candidate ranking by fit strength

This starter spec intentionally excludes:
- UI requirements
- full explainability UX
- integrations
- advanced orchestration features

## 1.1 Guiding Principles

The MVP implementation should follow these principles:
- Evidence over opinion: ranking and reason codes must be grounded in dataset fields and normalized matching logic.
- Human in the loop: outputs are decision support recommendations, not automatic staffing decisions.
- Explicit tradeoffs: when strengths and gaps coexist, scoring and reason codes should make that visible.
- Traceable by default: persist input role, scoring components, constraint outcomes, and final ranking for auditability.
- Safety and fairness by design: use role-relevant capability and logistics signals only; ignore names and protected attributes.
- Evidence tiers, not over-claims: keep confirmed and potential evidence separate. Confirmed evidence affects scoring. Potential evidence is review-only and never auto-counted as requirement coverage.

## 2. Inputs and Data Sources

### Required input
- A job description or role posting (free text or role record)

### Dataset sources
- `dataset/role_requirements_train.csv`
- `dataset/consultant_profiles_train.csv`
- `dataset/historical_matches_train.csv` (optional scoring calibration signal)
- `dataset/data_dictionary.csv` (schema and column reference)

### Join keys
- `role_id`
- `consultant_id`

## 3. Core Output

Given one role/job posting, return:
- ranked consultants (top N, default N=10)
- numeric fit score per consultant (0-100)
- rank position (1..N)
- short reason codes tied to matched and missing requirements
- recommendation-only posture suitable for human review and override

## 4. Comparison Scope

Each consultant is compared to the role on these dimensions:
1. Required skills coverage (highest priority)
2. Required certifications and required tools
3. Domain experience relevance
4. Preferred skills coverage
5. Experience/seniority fit
6. Behavioral fit using role importance weights
7. Availability and location feasibility
8. Prior client rating (if present)

Must-have constraints are hard rules and override weighted ranking.

## 4.1 Componentized Model Split

The MVP model stack is split into five components with explicit handoffs:
1. candidate-discover: scans consultant batches and returns potentially relevant candidates.
2. candidate-fit-evaluator: evaluates one consultant against one role and emits a standardized Evaluation Packet.
3. deterministic-scoring-agent: computes component scores, constraints, and final rank ordering.
4. rank-comparison-agent: explains already-computed rank order and score deltas.
5. resume-upskill-advisor: gives consultant-specific role-positioning and realistic upskill suggestions.

Boundary rule:
- Only the deterministic-scoring-agent is authoritative for ranking outcomes.
- The comparison and upskill components are explanatory and advisory only.

## 5. Preprocessing and Normalization

Before scoring:
1. Parse multi-value fields using `|` delimiter.
2. Normalize case and whitespace for all text comparisons.
3. Apply controlled alias mapping (for example: `K8s` -> `Kubernetes`, `Node` -> `Node.js`, `CI Integration` -> `CI/CD`).
4. Treat blank values as unknown/not available, never as zero.
5. Enrich confirmed evidence from both structured fields and normalized free text (`resume_text`, `project_experience_summary`, `notes`) using exact normalized phrase matching.
6. Compute potential evidence cues for still-missing requirements using loose matching (related tool hints, partial token overlap, and soft lexical similarity).
7. Persist evidence provenance and tier (`confirmed` or `potential_unconfirmed`) per requirement for auditability.

## 6. Constraint Gate (Hard Rule Stage)

Evaluate explicit `must_have_constraints` before weighted scoring.

If a consultant violates any must-have constraint:
- either exclude from rankable pool, or
- cap to bottom tier with a violation flag

Examples of must-have checks:
- mandatory certification
- hard minimum years of experience
- mandatory domain requirement
- onsite/hybrid feasibility by simplified geography rule
- start-date feasibility
- explicit work authorization/sponsorship rule

## 7. Fit Scoring Model (Weighted Stage)

For consultants that pass the constraint gate, calculate a weighted fit score.

Suggested weighted model (0-100 scale):

- Required skills: 40
- Required certifications/tools: 15
- Domain experience: 12
- Preferred skills: 10
- Experience fit: 8
- Behavioral fit: 8
- Availability/location fit: 5
- Prior client rating: 2

Formula:

`fit_score = sum(weight_i * normalized_component_i)`

Where each `normalized_component_i` is in `[0,1]`.

### Component guidance
- Required skills: ratio of required skills matched.
- Required certifications/tools: ratio matched; missing mandatory item heavily penalized.
- Domain experience: full credit for exact domain, partial credit for mapped adjacent domains.
- Preferred skills: ratio of preferred skills matched.
- Experience fit: full credit if consultant meets target band; partial if near miss.
- Behavioral fit: weighted by role importance columns.
- Availability/location: credit for feasible start and logistics alignment.
- Prior client rating: use only when available; unknown remains neutral.

Evidence-tier rule:
- Only `confirmed` evidence contributes to numeric component scores.
- `potential_unconfirmed` evidence never increases fit score and never clears a hard requirement.

## 8. Ranking Logic

1. candidate-discover builds a potential candidate pool.
2. candidate-fit-evaluator produces one Evaluation Packet per candidate-role pair.
3. deterministic-scoring-agent applies hard constraint gate and weighted fit scoring.
4. Sort descending by fit score.
5. Apply deterministic tie-breakers in order:
   - higher required skill coverage
   - fewer must-have risk flags
   - better required certification/tool coverage
   - earlier feasible availability date
6. rank-comparison-agent generates human-readable ranking comparisons.
7. Return top N with score breakdown, reason codes, and optional advisory outputs.

## 9. Reason Codes for Comparison and Ranking

Every ranked result should include compact reason codes, for example:
- `REQ_SKILLS_STRONG`
- `REQ_CERT_MISSING_AZ104`
- `DOMAIN_PARTIAL_FIT_FINTECH_BANKING`
- `EXP_BELOW_TARGET_BY_1Y`
- `CONSTRAINT_FAIL_ONSITE_STATE_MISMATCH`

Also include review-only potential signals when relevant, for example:
- `REVIEW_POTENTIAL_SKILL_AIRFLOW`
- `REVIEW_POTENTIAL_TOOL_SNOWFLAKE`
- `REVIEW_POTENTIAL_CERT_AWS_CERTIFIED`

Interpretation rule:
- `GAP_*` and `CONSTRAINT_FAIL_*` remain authoritative for requirement status.
- `REVIEW_POTENTIAL_*` indicates adjacent evidence that should be discussed with the candidate and validated by recruiter/interviewer.

Reason codes must be generated from dataset fields, not free-form opinion.

## 10. Baseline Validation

Minimum validation for this starter spec:
1. For a selected `role_id`, produce a deterministic top-10 ranking.
2. Confirm any must-have violations are excluded or bottom-capped consistently.
3. Verify score stability across repeated runs with same inputs.
4. Compare top-ranked outputs against historical outcomes as a sanity check, while treating historical human scores as noisy signal.
5. Verify strict evidence behavior: potential signals do not change fit score or remove missing-gap flags.
6. Verify review-only behavior: potential signals are present only when corresponding requirements remain unconfirmed.

## 11. Non-Goals (Current Starter Scope)

Not included in this spec phase:
- full narrative explanation generation
- side-by-side visual comparison screens
- fairness dashboarding
- production policy, auth, or deployment architecture

This document defines only the baseline mechanics for role-to-consultant comparison and fit-based ranking.