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

## Working Streamlit MVP

The Streamlit app includes:

- Persistent SQLite-backed investigations database.
- Investigation creation and editing.
- Evidence metadata capture.
- CAPA creation and register.
- Executive dashboard with charts and metrics.
- AI investigation assistant with OpenAI support when `OPENAI_API_KEY` is set.
- Offline deterministic AI fallback when no API key is present.
- Downloadable Markdown executive RCA reports.
- Audit log and product readiness page.

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

The app is moving from demo toward product: dashboard-first enterprise interface, manufacturing RCA workflows, CAPA management, investigation quality scoring, AI assistant surfaces, reporting, evidence tracking, audit logging, and settings/readiness for future enterprise configuration.

## Future AI Integration

AI outputs are modeled around evidence considered, findings, confidence, missing data, and recommended next steps. The app avoids exposing hidden chain-of-thought. Future backend work can add retrieval over historical investigations, report generation, voice interviews, and multi-agent investigation workflows.
