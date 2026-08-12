# Squad 1 - 10 Minute Presentation Script (Role-Based)

Goal: deliver a confident, business-first story with a working prototype.

Challenge: AI Consultant Selection Assistant

Total time: 10:00 maximum

Team roles:
- Speaker 1: David Luo (Business Analyst)
- Speaker 2: Lucas Michalski (Developer)
- Speaker 3: Maheep Chawla (Developer)
- Speaker 4: Alhassan Diallo (DevOps/Operations)

## Slide-by-Slide Timeline

## 0:00-0:45 | Opening and Problem Context
Speaker: David

Script:
"Good afternoon judges. We are Squad 1. Today we are presenting an AI Consultant Selection Assistant.
The current process for consultant selection is often manual, subjective, and slow, even though skills data already exists.
Our goal was to deliver a credible proof of concept that automatically screens and ranks applicants while keeping final decisions with human reviewers."

## 0:45-1:45 | User and Success Criteria
Speaker: David

Script:
"Our primary user is a staffing manager or account manager responsible for consultant matching.
Their job-to-be-done is to identify the best-fit consultants quickly and justify the choice with evidence.
We defined success as reducing time to first shortlist from about 30 minutes to under 5 minutes with transparent rationale.
We also included certifications and behavioral assessment signals to better align role-fit decisions with real staffing practices.
For this hackathon, we intentionally scoped to one core workflow to ensure quality and reliability."

## 1:45-3:00 | Solution Overview and AI Approach
Speaker: Lucas

Script:
"Our solution is the Squad 1 Consultant Match Assistant.
At a high level, users submit a role request with must-have skills, certifications, behavioral preferences, and constraints.
The system uses a hybrid approach: deterministic ranking for consistency, retrieval for evidence, and LLM reasoning for explainability.
It returns a ranked shortlist with fit scores, matched skills, skill-gap flags, and confidence indicators.
This gives speed, transparency, and better decision quality while keeping humans in charge."

## 3:00-6:00 | Live Demo
Speaker: Maheep (primary), Alhassan (backup)

Demo sequence:
1. Show role intake screen and enter must-have and preferred skills.
2. Submit prepared "Cloud Support Engineer" request.
3. Show ranked top 5 candidates with fit score breakdown, including certification and behavioral fit.
4. Open one candidate explanation: matched skills, gaps, and evidence snippets.
5. Show edge case where no strong match exists and system raises a human-review warning.

Live script (short prompts):
- "Here is a real role request with practical staffing constraints."
- "The assistant now returns a structured top-5 shortlist in seconds."
- "Each recommendation includes evidence, confidence, certification match, and explicit skill gaps."
- "When confidence is low, the workflow flags this for human review rather than forcing a decision."

If demo fails:
- Switch to backup screenshots/video within 10 seconds.
- Script: "We captured a full successful run earlier; here is the same workflow and output."

## 6:00-7:15 | Architecture and Build Choices
Speaker: Lucas

Script:
"We designed for speed and reliability.
The architecture has a lightweight UI, an orchestration API, deterministic scoring logic, retrieval, and a pluggable AI adapter.
This let us validate quickly with synthetic data first, then connect to Foundry once access was available.
We designed the data model to align with existing consultant tracker and Power BI dimensions, which reduces onboarding friction.
We intentionally avoided over-engineering to focus on measurable business outcomes."

## 7:15-8:15 | Operations and Reliability Readiness
Speaker: Alhassan

Script:
"From an operations perspective, we prioritized demo reliability and team execution.
We used clear integration contracts, milestone checkpoints, and smoke tests.
We prepared fallback assets and a backup presenter path to reduce delivery risk.
Although CI/CD was not required for this event, our modular design is ready for future pipeline adoption.
We also added guardrails: low-confidence flags, evidence-backed rationale, and human-in-the-loop review before final selection.
From a US perspective, we frame this as AI-assisted decision support with traceability and reviewer accountability."

## 8:15-9:15 | Business Value, Assumptions, and Limitations
Speaker: David

Script:
"Expected value from this prototype is faster staffing decisions and better consistency.
Our target is reducing shortlist turnaround from approximately 30 minutes to less than 5 minutes per request.
Key assumptions were that profile data is reasonably current and role requirements are sufficiently detailed.
Current limitations are synthetic sample data and limited direct integration with production consultant trackers and resume databases.
Even with these limits, this proof of concept demonstrates clear business feasibility."

## 9:15-10:00 | Roadmap and Close
Speaker: Alhassan

Script:
"Our recommended next steps are:
1) connect to live consultant profile trackers and resume databases,
2) strengthen evaluation, fairness checks, and governance,
3) operationalize with reporting views, including Power BI-aligned monitoring.
In summary, Squad 1 built a focused AI prototype that addresses a real business challenge with clear practical value.
Thank you, and we welcome your questions."

---

## Q&A Cheat Sheet (Prepare Answers)

### Q1: Why did you choose this AI approach?
Answer:
"We matched the approach to the challenge. Deterministic scoring improves consistency, RAG adds evidence grounding, and agentic orchestration supports a multi-step staffing workflow with human oversight."

### Q2: How do you know this creates business value?
Answer:
"We defined a clear metric: time to first shortlist. The workflow is designed to reduce this from around 30 minutes to under 5 minutes while improving explainability."

### Q3: What are the biggest risks?
Answer:
"Data quality, fairness perception, and integration depth. We reduced risk with structured scoring, transparent rationale per candidate, human review checkpoints, and clear AI-assisted decision framing."

### Q4: How would you productionize this?
Answer:
"Add production tracker and resume integrations, model and prompt evaluation, security controls, monitoring, and CI/CD. The current architecture is modular, so we can scale in controlled phases."

### Q5: What did your team do to ensure delivery?
Answer:
"We used strict timeboxing, milestone gates, integration ownership, and a fallback demo path. That kept the prototype stable and presentation-ready under hackathon constraints."

---

## Rehearsal Checklist

- [ ] Each speaker stays within assigned time.
- [ ] Demo path completes in under 3 minutes.
- [ ] Backup demo assets open instantly.
- [ ] Business metric is stated clearly.
- [ ] Every team member can answer one technical and one business question.

## Fill-In Blanks Before Presenting

- Challenge statement: AI Consultant Selection Assistant
- Persona: Staffing manager / account manager
- Key metric: Time to first shortlist (target: <= 5 minutes)
- AI pattern used: Hybrid (deterministic ranking + RAG + LLM explainability)
- Top value claim: Faster, more transparent consultant matching decisions
- Main limitation: Synthetic sample data and limited direct integrations to live tracker/resume systems
