# RCA Project Chat Notes

## 2026-06-06

- The original React app was identified as a polished prototype, not a functional product.
- A working Streamlit MVP was added with SQLite persistence, investigations, evidence, CAPA, AI assistant, reporting, and audit log.
- Streamlit Cloud deployment files were added to GitHub:
  - `streamlit_app.py`
  - `requirements.txt`
  - `.streamlit/config.toml`
- The product direction was corrected to emphasize RCA and Lean tools instead of manual form entry.
- Added RCA Toolbox requirements:
  - 5 Why analysis
  - 5M+1E analysis
  - Lean strategy recommendations
  - AI-generated CAPAs
  - One-click CAPA creation from generated recommendations

Note: Codex/ChatGPT conversations are not automatically written into project folders unless we explicitly create or update files. This file is the project-facing record for the RCA-related decisions from this thread.

## Project Note Policy

- Future meaningful product decisions, feature changes, deployment fixes, and go-to-market direction should be summarized in this file.
- The chat itself still lives in the Codex/ChatGPT chat history, but project-facing decisions should be copied here so the RCA project folder remains useful.
- The app entry point remains `streamlit_app.py` at the repository root so Streamlit Cloud can deploy it.

## Go-To-Market RCA Update Summary

- Added Guided Investigation interview flow to reduce blank-form manual entry.
- Added Investigation Workspace with visual RCA map, method recommendations, CAPA quality checker, and closure gates.
- Expanded RCA Toolbox with 5 Why, 5M+1E, FMEA starter, Pareto starter, fault-tree starter, Lean strategy, and generated CAPAs.
- Added a 20-method RCA library covering common business RCA methods such as 8D, A3, DMAIC, PDCA, Is/Is Not, change analysis, barrier analysis, process mapping/SIPOC, event timelines, control charts, scatter analysis, check sheets, current reality tree, and bowtie analysis.
- Added CAPA quality checker to flag weak actions such as training-only fixes.
- Added closure readiness scoring and RCA-method output in executive reports.
