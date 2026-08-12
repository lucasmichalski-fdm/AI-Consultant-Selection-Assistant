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

## 5. Preprocessing and Normalization

Before scoring:
1. Parse multi-value fields using `|` delimiter.
2. Normalize case and whitespace for all text comparisons.
3. Apply controlled alias mapping (for example: `K8s` -> `Kubernetes`, `Node` -> `Node.js`, `CI Integration` -> `CI/CD`).
4. Treat blank values as unknown/not available, never as zero.
5. Optionally enrich consultant skill tokens from `resume_text` when structured skill fields are sparse.

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

## 8. Ranking Logic

1. Build candidate pool.
2. Apply hard constraint gate.
3. Compute weighted fit for remaining candidates.
4. Sort descending by fit score.
5. Apply deterministic tie-breakers in order:
   - higher required skill coverage
   - fewer must-have risk flags
   - better required certification/tool coverage
   - earlier feasible availability date
6. Return top N with score breakdown and reason codes.

## 9. Reason Codes for Comparison and Ranking

Every ranked result should include compact reason codes, for example:
- `REQ_SKILLS_STRONG`
- `REQ_CERT_MISSING_AZ104`
- `DOMAIN_PARTIAL_FIT_FINTECH_BANKING`
- `EXP_BELOW_TARGET_BY_1Y`
- `CONSTRAINT_FAIL_ONSITE_STATE_MISMATCH`

Reason codes must be generated from dataset fields, not free-form opinion.

## 10. Baseline Validation

Minimum validation for this starter spec:
1. For a selected `role_id`, produce a deterministic top-10 ranking.
2. Confirm any must-have violations are excluded or bottom-capped consistently.
3. Verify score stability across repeated runs with same inputs.
4. Compare top-ranked outputs against historical outcomes as a sanity check, while treating historical human scores as noisy signal.

## 11. Non-Goals (Current Starter Scope)

Not included in this spec phase:
- full narrative explanation generation
- side-by-side visual comparison screens
- fairness dashboarding
- production policy, auth, or deployment architecture

This document defines only the baseline mechanics for role-to-consultant comparison and fit-based ranking.