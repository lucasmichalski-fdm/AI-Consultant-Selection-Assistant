# Starter Task Brief - AI Consultant Selection Assistant (US Perspective)

**Hackathon challenge: Sales - AI Consultant Selection Assistant**

Welcome! Your team is building an AI-powered assistant for the sales managers of *Company A*, a fictional US IT consulting and staffing firm. Everything in this dataset is fully synthetic - no real people, clients, or companies.

---

## 1. Business context

Company A's sales managers fill client roles from a bench of consultants. Today the process is manual: a manager reads a client role request, skims dozens of consultant profiles and resumes, applies gut feel, and submits a shortlist. It is slow, inconsistent, and occasionally unfair - strong candidates get missed because their profile was messy, and familiar faces get picked over better fits.

Your mission: build an assistant that, given a **role** and the **consultant pool**, produces a **ranked, explained, constraint-aware shortlist** a sales manager can trust and send onward - in seconds, not hours.

The solution does not need to be production-grade. A convincing MVP that ranks well, explains itself clearly, respects hard constraints, and avoids biased attributes will score well with the judges.

## 2. Dataset overview

| File | Rows | What it is |
|---|---|---|
| `consultant_profiles_train.csv` | 240 | The consultant bench. IDs `C-001`-`C-240`, 10 role archetypes (Business Analyst, QA Analyst, DevOps Engineer, Full Stack Developer, Data Engineer, Cloud Engineer, AI Engineer, Scrum Master, Product Analyst, SDET), junior through senior. |
| `role_requirements_train.csv` | 20 | Open client roles. IDs `R-001`-`R-020` across Banking, Insurance, Healthcare, Retail, Energy, Telecom, Public Sector, FinTech, Logistics, and Manufacturing. Each includes skills, certifications, behavioral importance weights, logistics, and `must_have_constraints`. |
| `historical_matches_train.csv` | 200 | The **last manual staffing cycle** for these same 20 roles: 10 considered consultants per role, who was shortlisted, who was selected (exactly one per role), client feedback, and recruiter reasoning. |
| `data_dictionary.csv` | 81 | Every column of every file above: type, meaning, example, and intended use. **Read this first.** |

**Join keys:** `consultant_id` (`C-###`) and `role_id` (`R-###`) link `historical_matches_train.csv` to the other two files. `historical_match_id` (`HM-###`) is just a row key.

### About the historical data - learn from it, including the mistakes

The historical file shows how the *manual* process handled these 20 roles. It contains real signal (skill alignment, domain fit, availability, ratings all correlate with `match_score_assigned_by_human` and outcomes) **and deliberate human imperfection**:

- Some selections were driven by familiarity, interview polish, or bill rate rather than fit - and the `client_feedback_score` / `placement_success` columns show those placements underperforming. The `reason_selected_or_rejected` text is candid about why.
- At least one strong candidate was passed over simply because their profile was under-documented at submission time; look for the retrospective in `outcome_notes`.
- `match_score_assigned_by_human` is a noisy 1-10 gut-feel score - useful training signal, **not** ground truth.

A great demo moment: show where your assistant would have disagreed with the humans, and why.

## 3. Suggested MVP features

1. **Role-to-candidate ranking** - given a `role_id`, return a ranked top 5-10 with scores.
2. **Explainable recommendations** - for each candidate: why they rank where they do, citing specific skills, domains, certifications, behavioral fit, and logistics from the data.
3. **Skill-gap analysis** - what is missing vs required/preferred skills, certs, and tools; distinguish "hard blocker" from "coachable gap."
4. **Constraint checking** - parse `must_have_constraints` and cap or exclude violators (work authorization, hard experience minimums, certifications, onsite/hybrid feasibility, start-by dates, mandatory domain experience) *even when the candidate is otherwise excellent*, and say so explicitly.
5. **Data-quality awareness** - detect blank behavioral scores, missing ratings, and messy `resume_text`; lower confidence and flag rather than silently guessing. Bonus: mine `resume_text` for skills missing from structured fields.
6. **Comparison view** - side-by-side comparison of any two consultants for a role.
7. **Client-ready shortlist summary** - a short writeup a sales manager could forward.

## 4. Suggested ranking factors

Judges score your rankings against a hidden weighted rubric. The exact weights are not disclosed, but the factor list and priority order below is a strong guide:

1. **Required skills coverage** - the dominant factor by a wide margin.
2. **Required certifications and required tools** - substantial weight.
3. **Domain experience** - substantial weight; closely related domains (e.g., Banking <-> FinTech, Healthcare <-> Insurance) deserve partial credit unless the role lists domain as a must-have.
4. **Preferred skills** - moderate weight.
5. **Years of experience / seniority fit** - moderate weight.
6. **Behavioral fit** - moderate weight, weighted by the role's five `*_importance` columns (a 2.3/5 communication score matters a lot when `communication_importance` is 4+).
7. **Availability + location/remote/relocation fit** - smaller weight, but still visible in rankings.
8. **Prior client rating** - smaller weight; treat blank as "unknown," not zero.

**Must-have constraints override everything.** A candidate violating any must-have should be capped near the bottom or excluded with the violated rule named - no matter how strong they look otherwise.

## 5. Explainability expectations

Every recommendation should answer: *why this person, why this rank, what's missing, what's risky, and what should the interviewer probe?* Good explanations cite the data ("covers all 5 required skills; holds Terraform Associate; 9 yrs vs 8 required; available 2026-08-31") rather than vibes ("great culture fit"). If your system uses an LLM, ground its claims in retrieved profile fields.

## 6. Bias and fairness expectations

- The data intentionally contains **no protected demographic attributes** (race, gender, age, religion, disability, marital status, national origin, ethnicity). Do not infer or fabricate them.
- **Names must not influence ranking.** `first_name`/`last_name` are display-only. Judges will probe this.
- Location may be used **only** for logistics feasibility (onsite/hybrid/relocation/time zone) - never as a proxy for anything else.
- Work authorization may be used **only** to check explicit sponsorship constraints in `must_have_constraints`.
- Be able to state, on demand, which attributes your ranking uses and which it deliberately ignores.

## 7. Example queries your assistant should handle

- "Find the top 5 consultants for Role R-003 and explain why."
- "Which consultants are nearly qualified but have skill gaps?"
- "Compare Consultant C-014 and C-052 for this role."
- "Show me the ranking factors for each shortlisted consultant."
- "Flag any missing or low-confidence profile data."
- "Explain how the recommendation avoids biased attributes."

(For the comparison query, pick any role you like - part of the test is handling an under-specified ask gracefully.)

## 8. Suggested demo flow (aim for ~5 minutes)

1. **30 sec** - one-slide problem framing: manual matching is slow, inconsistent, sometimes unfair.
2. **90 sec** - live: pick a role (e.g., `R-003` or `R-005`), generate the ranked shortlist with explanations.
3. **60 sec** - constraint handling: show a strong-looking candidate being capped/excluded for a must-have violation, with the rule named.
4. **60 sec** - skill gaps + data quality: a near-miss candidate with a coachable gap, and a messy/incomplete profile handled with lowered confidence (bonus: skills recovered from `resume_text`).
5. **45 sec** - fairness: show the attributes used vs ignored; demonstrate names don't move rankings.
6. **15 sec** - the payoff: hours to seconds, consistent, auditable. Judges will then run their own hidden evaluation queries against your system.

## 9. Data quirks to know before you build

- **Multi-value fields are pipe-separated** (`Python|SQL|Azure`). Fields containing commas are quoted; no newlines inside cells.
- **Blank means "not available," never zero** - blank behavioral scores, ratings, or education are incomplete data, not bad data.
- **Skill vocabulary has minor aliasing** (e.g., "CI Integration" vs "CI/CD", "K8s" vs "Kubernetes", "Node" vs "Node.js") - normalize before matching. Matching is case-insensitive.
- **Some resumes are deliberately messy** - lowercase fragments, "see attached," skills present in `resume_text` but absent from structured fields. This is by design.
- **Logistics are simplified to the state level** - treat a candidate as commutable for onsite/hybrid work if their `location_state` matches the role's state (for the NYC metro, NY/NJ/CT all count). Real geography is fuzzier; the ground truth uses this simplification.
- Dates are `YYYY-MM-DD`. "Today" for the challenge is **2026-08-07**.

Good luck - build something a skeptical sales manager would actually trust.
