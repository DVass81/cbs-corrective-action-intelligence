# CBS CAI Product Roadmap

This repo now contains two product tracks:

- The React/Vite app remains the polished enterprise prototype.
- `streamlit_app.py` is the working MVP app with persistence, forms, AI-ready analysis, audit log, CAPA tracking, evidence metadata, and report export.

## MVP Completed

- SQLite-backed investigations database.
- Seeded manufacturing RCA/CAPA examples.
- Investigation creation and editing.
- Evidence metadata capture.
- CAPA creation and register.
- Executive dashboard with cost, status, Pareto, RCA score, and overdue signals.
- AI assistant that uses `OPENAI_API_KEY` when available and a deterministic fallback otherwise.
- Downloadable Markdown executive RCA report.
- Audit log for investigation, evidence, and CAPA events.
- Product-readiness admin page.

## Next Commercial Milestones

1. Replace demo sign-in with real authentication.
2. Add role-based authorization for admins, investigators, approvers, executives, and auditors.
3. Store uploaded evidence files in durable object storage.
4. Add approval workflow and closure gates.
5. Generate PDF and Word reports.
6. Add ERP, QMS, MES, email, Teams, Slack, SharePoint, and Power BI integrations.
7. Add multi-tenant organization/account model.
8. Add monitoring, backups, CI/CD, test coverage, and deployment scripts.
9. Create pricing, onboarding, support docs, and security/compliance collateral.

## Run The Streamlit MVP

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
