# AI Tutor Beta — 14-Day Validation Pilot Engine

A lean, verification-first platform for the CUET General Test section. This codebase is dedicated entirely to testing the **Linear Priority Feedback Loop** using manually curated resources.

## 🚀 Environment Initialization
Run the database cluster locally using:
```bash
docker-compose up -d
```
- **Postgres Core Coordinates:** `localhost:5432` | User: `aitutor_user` | Database: `aitutor_beta_state`

## 📊 Workstreams
- **🧑‍💻 Engineer A (Content/AI):** Handles structured quiz payload configurations via Pydantic (`pipelines/content_seeding/`) and wires up the unified single-model LLM tutor explanation interfaces.
- **🧑‍💻 Engineer B (Backend/State):** Implements the local Postgres schema relationships and writes the deterministic calculation metrics rule: `Priority = (Weakness * 0.40) + (PrerequisiteImportance * 0.25) + (ReviewDue * 0.20) + (ExamImportance * 0.15)`.
