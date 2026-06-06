# CBS Corrective Action Intelligence (CAI)

CBS Corrective Action Intelligence is a production-shaped RCA, CAPA, Lean improvement, and organizational learning platform for manufacturing teams.

Tagline: Find the Cause. Fix the System. Prevent Recurrence.

## Streamlit Cloud Deployment

Use this exact main file path in Streamlit Cloud:

```text
streamlit_app.py
```

Streamlit Cloud will install dependencies from:

```text
requirements.txt
```

RCA-specific notes and project material live in the `RCA/` folder. The app entry point stays at the repository root so Streamlit Cloud can find it.

## Working Streamlit MVP

The Streamlit app includes:

- Persistent SQLite-backed investigations database.
- Guided investigation interview that drafts problem statements.
- Investigation Workspace with case summary, visual RCA map, method selection, CAPA quality, and closure gates.
- RCA Toolbox with 5 Why, 5M+1E, FMEA starter, Pareto starter, fault-tree starter, and generated CAPAs.
- RCA method library covering 5 Whys, fishbone, 5M+1E/6M, Pareto, FMEA, fault tree, 8D, A3, DMAIC, PDCA, Is/Is Not, change analysis, barrier analysis, SIPOC/process mapping, event timelines, control charts, scatter analysis, check sheets, current reality tree, and bowtie analysis.
- Lean strategy recommendations by issue type.
- AI-generated corrective, preventive, containment, and verification actions.
- One-click creation of generated CAPA records.
- CAPA quality checker that flags weak actions such as training-only fixes.
- Closure readiness scoring.
- AI investigation assistant with OpenAI support when `OPENAI_API_KEY` is set.
- Offline deterministic fallback when no API key is present.
- Downloadable executive RCA reports with RCA method output included.

Run locally:

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Optional AI setup:

```bash
set OPENAI_API_KEY=your_api_key_here
set CAI_OPENAI_MODEL=gpt-4.1-mini
streamlit run streamlit_app.py
```

## React Prototype

The original React/Vite prototype remains in the repo as the polished front-end concept.

```bash
npm install
npm run dev
```

## Product Scope

The app is moving from demo toward product: dashboard-first enterprise interface, manufacturing RCA workflows, guided investigation, 5 Why, 5M+1E, Lean countermeasure selection, generated CAPA management, investigation quality scoring, AI assistant surfaces, reporting, evidence tracking, audit logging, and settings/readiness for future enterprise configuration.

## Future AI Integration

AI outputs are modeled around evidence considered, findings, confidence, missing data, and recommended next steps. The app avoids exposing hidden chain-of-thought. Future backend work can add retrieval over historical investigations, report generation, voice interviews, and multi-agent investigation workflows.
