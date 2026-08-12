# AI-Consultant-Selection-Assistant

This repository now includes a lightweight applicant-screening engine in `/home/runner/work/AI-Consultant-Selection-Assistant/AI-Consultant-Selection-Assistant/consultant_selection.py` that:

- grades and ranks consultants against a job profile,
- produces explainable recommendations,
- highlights missing required and preferred skills/certifications.

## Core API

- `JobDescription`: required skills, preferred skills, required certifications, behavioral thresholds
- `Applicant`: candidate profile data
- `rank_applicants(job_description, applicants)`: returns ranked `ApplicantRanking` results

## Run tests

```bash
python -m unittest tests/test_consultant_selection.py -v
```
