from __future__ import annotations

import json
import os
import sqlite3
from contextlib import closing
from datetime import date, datetime
from pathlib import Path
from typing import Any

import pandas as pd
import plotly.express as px
import streamlit as st

APP_NAME = "CBS Corrective Action Intelligence"
DB_PATH = Path(os.getenv("CAI_DB_PATH", "data/cai_product.db"))

STATUSES = [
    "New",
    "Assigned",
    "Containment",
    "Investigation",
    "Root Cause Identified",
    "Corrective Action",
    "Verification",
    "Closed",
]
SEVERITIES = ["Low", "Medium", "High", "Critical"]
TYPES = ["Quality", "Safety", "Delivery", "Downtime", "Supplier", "Engineering"]
CAPA_STATUSES = ["Open", "Assigned", "In Progress", "Completed", "Verified", "Closed"]

DEMO_CASES = [
    {
        "case_number": "CAI-2026-001",
        "title": "Incorrect Copper Material Ordered",
        "department": "Purchasing",
        "process": "Raw material planning",
        "product": "Copper bus bar",
        "customer": "Internal production",
        "supplier": "Midwest Metals",
        "detection_date": "2026-05-08",
        "owner": "Maria Chen",
        "status": "Corrective Action",
        "severity": "High",
        "case_type": "Supplier",
        "cost_impact": 84200,
        "rca_score": 86,
        "repeat_issue": 1,
        "problem": "C110 copper was ordered instead of C101 copper for a high-conductivity assembly, causing production hold and expedited replacement material.",
        "root_cause": "ERP item master allowed substitute material without engineering approval gate.",
        "corrective_action": "Lock controlled alloy fields and require engineering approval for substitutions.",
        "due_date": "2026-06-14",
    },
    {
        "case_number": "CAI-2026-002",
        "title": "Customer Complaint on Commutator Quality",
        "department": "Quality",
        "process": "Final inspection",
        "product": "Motor commutator",
        "customer": "Northline Drives",
        "supplier": "Internal machining",
        "detection_date": "2026-05-12",
        "owner": "Andre Miller",
        "status": "Verification",
        "severity": "Critical",
        "case_type": "Quality",
        "cost_impact": 126000,
        "rca_score": 91,
        "repeat_issue": 0,
        "problem": "Customer reported elevated brush wear traced to commutator surface finish above specification on two shipped lots.",
        "root_cause": "Grinding wheel dressing interval was extended without capability validation.",
        "corrective_action": "Restore controlled dressing interval and add SPC trigger for surface finish drift.",
        "due_date": "2026-06-10",
    },
    {
        "case_number": "CAI-2026-003",
        "title": "Machine Downtime Event",
        "department": "Maintenance",
        "process": "CNC turning cell",
        "product": "Shaft assembly",
        "customer": "Internal assembly",
        "supplier": "OEM service",
        "detection_date": "2026-05-18",
        "owner": "Priya Shah",
        "status": "Investigation",
        "severity": "High",
        "case_type": "Downtime",
        "cost_impact": 48900,
        "rca_score": 73,
        "repeat_issue": 1,
        "problem": "CNC lathe L-14 stopped repeatedly during second shift due to servo overload alarms, creating 9.5 hours of unplanned downtime.",
        "root_cause": "Likely lubrication restriction and missing TPM inspection point.",
        "corrective_action": "Add lubrication flow check to weekly TPM and replace restricted metering valve.",
        "due_date": "2026-06-08",
    },
]


def connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def execute(sql: str, params: tuple[Any, ...] = ()) -> None:
    with closing(connect()) as conn:
        conn.execute(sql, params)
        conn.commit()


def read_df(sql: str, params: tuple[Any, ...] = ()) -> pd.DataFrame:
    with closing(connect()) as conn:
        return pd.read_sql_query(sql, conn, params=params)


def read_one(sql: str, params: tuple[Any, ...] = ()) -> dict[str, Any] | None:
    with closing(connect()) as conn:
        row = conn.execute(sql, params).fetchone()
        return dict(row) if row else None


def audit(event_type: str, description: str, case_id: int | None = None) -> None:
    execute(
        """
        insert into audit_log (case_id, event_type, description, actor, created_at)
        values (?, ?, ?, ?, ?)
        """,
        (case_id, event_type, description, st.session_state.get("actor", "Demo User"), datetime.utcnow().isoformat()),
    )


def init_db() -> None:
    with closing(connect()) as conn:
        conn.executescript(
            """
            create table if not exists investigations (
                id integer primary key autoincrement,
                case_number text unique not null,
                title text not null,
                department text not null,
                process text,
                product text,
                customer text,
                supplier text,
                detection_date text,
                owner text,
                status text not null,
                severity text not null,
                case_type text not null,
                cost_impact real default 0,
                rca_score integer default 50,
                repeat_issue integer default 0,
                problem text not null,
                root_cause text default '',
                corrective_action text default '',
                due_date text,
                created_at text not null,
                updated_at text not null
            );
            create table if not exists corrective_actions (
                id integer primary key autoincrement,
                case_id integer not null references investigations(id),
                title text not null,
                owner text not null,
                due_date text,
                status text not null,
                containment_action text default '',
                corrective_action text default '',
                preventive_action text default '',
                verification_method text default '',
                effectiveness_review_date text,
                created_at text not null,
                updated_at text not null
            );
            create table if not exists evidence (
                id integer primary key autoincrement,
                case_id integer not null references investigations(id),
                evidence_type text not null,
                title text not null,
                notes text default '',
                file_name text default '',
                created_at text not null
            );
            create table if not exists audit_log (
                id integer primary key autoincrement,
                case_id integer references investigations(id),
                event_type text not null,
                description text not null,
                actor text not null,
                created_at text not null
            );
            """
        )
        if conn.execute("select count(*) from investigations").fetchone()[0] == 0:
            now = datetime.utcnow().isoformat()
            for item in DEMO_CASES:
                conn.execute(
                    """
                    insert into investigations (
                        case_number, title, department, process, product, customer, supplier, detection_date,
                        owner, status, severity, case_type, cost_impact, rca_score, repeat_issue, problem,
                        root_cause, corrective_action, due_date, created_at, updated_at
                    ) values (
                        :case_number, :title, :department, :process, :product, :customer, :supplier, :detection_date,
                        :owner, :status, :severity, :case_type, :cost_impact, :rca_score, :repeat_issue, :problem,
                        :root_cause, :corrective_action, :due_date, :created_at, :updated_at
                    )
                    """,
                    {**item, "created_at": now, "updated_at": now},
                )
            cases = conn.execute("select id, case_number, owner, corrective_action, due_date from investigations").fetchall()
            for index, case in enumerate(cases, start=1):
                conn.execute(
                    """
                    insert into corrective_actions (
                        case_id, title, owner, due_date, status, containment_action, corrective_action,
                        preventive_action, verification_method, effectiveness_review_date, created_at, updated_at
                    ) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        case["id"],
                        f"CAPA for {case['case_number']}",
                        case["owner"],
                        case["due_date"],
                        CAPA_STATUSES[index - 1],
                        "Protect customer demand and quarantine suspect product or process outputs.",
                        case["corrective_action"],
                        "Update control plan, train owners, and monitor recurrence.",
                        "30-day recurrence check with layered process audit evidence.",
                        "2026-07-15",
                        now,
                        now,
                    ),
                )
            conn.commit()


def money(value: float | int) -> str:
    return f"${float(value):,.0f}"


def ai_fallback(case: dict[str, Any], evidence: pd.DataFrame) -> dict[str, Any]:
    missing = []
    if evidence.empty:
        missing.append("Objective evidence has not been attached yet.")
    if not case.get("root_cause"):
        missing.append("Root cause statement is incomplete.")
    if not case.get("corrective_action"):
        missing.append("Corrective action has not been defined.")
    if int(case.get("repeat_issue") or 0):
        missing.append("Prior occurrence search should be documented because this is marked as repeat.")
    confidence = max(35, min(95, int(case.get("rca_score") or 50) + (8 if not evidence.empty else -8)))
    return {
        "evidence_considered": evidence["title"].tolist() if not evidence.empty else ["Problem statement", "Case metadata"],
        "findings": [
            "The case should focus on process controls, verification evidence, and recurrence prevention.",
            "The current information is usable for triage but needs stronger objective evidence before closure.",
        ],
        "missing_data": missing or ["No obvious blockers found. Confirm effectiveness criteria before closure."],
        "recommended_next_step": "Add evidence, validate the root cause against facts, and define a measurable effectiveness check.",
        "confidence_level": confidence,
    }


def ai_analyze(case: dict[str, Any], evidence: pd.DataFrame) -> dict[str, Any]:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return ai_fallback(case, evidence)
    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        prompt = {
            "case": case,
            "evidence": evidence.to_dict(orient="records"),
            "instruction": "Return compact JSON with evidence_considered, findings, missing_data, recommended_next_step, confidence_level. Do not include hidden reasoning.",
        }
        response = client.responses.create(model=os.getenv("CAI_OPENAI_MODEL", "gpt-4.1-mini"), input=json.dumps(prompt))
        return json.loads(response.output_text.strip())
    except Exception as exc:
        result = ai_fallback(case, evidence)
        result["findings"].append(f"OpenAI analysis is not available in this environment: {exc}")
        return result


def sidebar() -> str:
    st.sidebar.title("CBS CAI")
    st.sidebar.caption("Corrective Action Intelligence")
    if "actor" not in st.session_state:
        st.session_state["actor"] = "Demo User"
    st.sidebar.text_input("Signed in as", key="actor")
    return st.sidebar.radio(
        "Workspace",
        [
            "Executive Dashboard",
            "Investigations",
            "New Investigation",
            "CAPA Management",
            "AI Assistant",
            "Reports",
            "Admin & Readiness",
        ],
    )


def dashboard() -> None:
    cases = read_df("select * from investigations order by detection_date desc")
    actions = read_df("select * from corrective_actions")
    open_cases = cases[cases["status"] != "Closed"]
    overdue = actions[(actions["status"] != "Closed") & (actions["due_date"] < date.today().isoformat())] if not actions.empty else actions
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Open Investigations", len(open_cases))
    c2.metric("Cost of Poor Quality", money(cases["cost_impact"].sum()))
    c3.metric("Average RCA Score", int(cases["rca_score"].mean()) if not cases.empty else 0)
    c4.metric("Overdue CAPAs", len(overdue))
    left, right = st.columns([1.2, 0.8])
    with left:
        pareto = cases.groupby("case_type", as_index=False).agg(count=("id", "count"), cost=("cost_impact", "sum"))
        st.plotly_chart(px.bar(pareto, x="case_type", y="count", color="cost", title="Issue Pareto"), use_container_width=True)
    with right:
        status = cases.groupby("status", as_index=False).size()
        st.plotly_chart(px.pie(status, names="status", values="size", title="Status Mix"), use_container_width=True)
    st.subheader("Risk Queue")
    st.dataframe(cases[["case_number", "title", "department", "owner", "status", "severity", "due_date", "cost_impact", "rca_score"]], use_container_width=True, hide_index=True)


def investigation_selector() -> tuple[pd.DataFrame, dict[str, Any] | None]:
    cases = read_df("select * from investigations order by detection_date desc, id desc")
    if cases.empty:
        st.info("No investigations yet.")
        return cases, None
    labels = [f"{row.case_number} - {row.title}" for row in cases.itertuples()]
    selected = st.selectbox("Investigation", labels)
    case_number = selected.split(" - ", 1)[0]
    return cases, read_one("select * from investigations where case_number = ?", (case_number,))


def investigations_page() -> None:
    cases, case = investigation_selector()
    if case is None:
        return
    st.dataframe(cases[["case_number", "title", "department", "owner", "status", "severity", "due_date", "cost_impact", "rca_score"]], use_container_width=True, hide_index=True)
    st.subheader(case["title"])
    with st.form("update_case"):
        col1, col2, col3 = st.columns(3)
        status = col1.selectbox("Status", STATUSES, index=STATUSES.index(case["status"]))
        owner = col2.text_input("Owner", value=case["owner"] or "")
        due_value = date.fromisoformat(case["due_date"]) if case["due_date"] else date.today()
        due_date = col3.date_input("Due date", value=due_value)
        problem = st.text_area("Problem statement", value=case["problem"], height=110)
        root_cause = st.text_area("Root cause", value=case["root_cause"] or "", height=90)
        corrective_action = st.text_area("Corrective action", value=case["corrective_action"] or "", height=90)
        rca_score = st.slider("Investigation quality score", 0, 100, int(case["rca_score"] or 50))
        submitted = st.form_submit_button("Save Investigation")
    if submitted:
        execute(
            """
            update investigations set status = ?, owner = ?, due_date = ?, problem = ?, root_cause = ?,
            corrective_action = ?, rca_score = ?, updated_at = ? where id = ?
            """,
            (status, owner, due_date.isoformat(), problem, root_cause, corrective_action, rca_score, datetime.utcnow().isoformat(), case["id"]),
        )
        audit("Investigation Updated", f"{case['case_number']} updated", case["id"])
        st.success("Investigation saved.")
        st.rerun()
    evidence_pagelet(case)


def evidence_pagelet(case: dict[str, Any]) -> None:
    st.subheader("Evidence")
    evidence = read_df("select * from evidence where case_id = ? order by created_at desc", (case["id"],))
    if not evidence.empty:
        st.dataframe(evidence[["evidence_type", "title", "notes", "file_name", "created_at"]], use_container_width=True, hide_index=True)
    with st.form(f"evidence_{case['id']}"):
        c1, c2 = st.columns(2)
        evidence_type = c1.selectbox("Evidence type", ["Photo", "ERP Record", "Inspection Record", "Interview", "Document", "Other"])
        title = c2.text_input("Title")
        notes = st.text_area("Notes")
        uploaded = st.file_uploader("Attach file metadata")
        if st.form_submit_button("Add Evidence"):
            execute(
                "insert into evidence (case_id, evidence_type, title, notes, file_name, created_at) values (?, ?, ?, ?, ?, ?)",
                (case["id"], evidence_type, title, notes, uploaded.name if uploaded else "", datetime.utcnow().isoformat()),
            )
            audit("Evidence Added", f"Evidence added: {title}", case["id"])
            st.success("Evidence added.")
            st.rerun()


def new_investigation_page() -> None:
    st.subheader("Create Investigation")
    next_number = f"CAI-{date.today().year}-{read_df('select id from investigations').shape[0] + 1:03d}"
    with st.form("new_investigation"):
        c1, c2, c3 = st.columns(3)
        case_number = c1.text_input("Case number", value=next_number)
        title = c2.text_input("Title")
        owner = c3.text_input("Owner")
        c4, c5, c6 = st.columns(3)
        department = c4.text_input("Department")
        severity = c5.selectbox("Severity", SEVERITIES, index=2)
        case_type = c6.selectbox("Type", TYPES)
        process = st.text_input("Process")
        product = st.text_input("Product")
        customer = st.text_input("Customer")
        supplier = st.text_input("Supplier")
        detection_date = st.date_input("Detection date", value=date.today())
        due_date = st.date_input("Due date", value=date.today())
        cost_impact = st.number_input("Estimated cost impact", min_value=0.0, value=0.0, step=1000.0)
        repeat_issue = st.checkbox("Repeat issue")
        problem = st.text_area("Problem statement", height=130)
        submitted = st.form_submit_button("Create Investigation")
    if submitted:
        now = datetime.utcnow().isoformat()
        execute(
            """
            insert into investigations (
                case_number, title, department, process, product, customer, supplier, detection_date, owner,
                status, severity, case_type, cost_impact, rca_score, repeat_issue, problem, root_cause,
                corrective_action, due_date, created_at, updated_at
            ) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, '', '', ?, ?, ?)
            """,
            (case_number, title, department, process, product, customer, supplier, detection_date.isoformat(), owner, "New", severity, case_type, cost_impact, 50, 1 if repeat_issue else 0, problem, due_date.isoformat(), now, now),
        )
        case = read_one("select id from investigations where case_number = ?", (case_number,))
        audit("Investigation Created", f"{case_number} created", case["id"] if case else None)
        st.success(f"{case_number} created.")


def capa_page() -> None:
    _, case = investigation_selector()
    if case is None:
        return
    with st.form("new_capa"):
        st.subheader("Create CAPA")
        title = st.text_input("CAPA title", value=f"Corrective action for {case['case_number']}")
        c1, c2, c3 = st.columns(3)
        owner = c1.text_input("Owner", value=case["owner"] or "")
        due_date = c2.date_input("Due date", value=date.today())
        status = c3.selectbox("Status", CAPA_STATUSES)
        containment = st.text_area("Containment action")
        corrective = st.text_area("Corrective action", value=case["corrective_action"] or "")
        preventive = st.text_area("Preventive action")
        verification = st.text_area("Verification method")
        review_date = st.date_input("Effectiveness review date", value=date.today())
        submitted = st.form_submit_button("Create CAPA")
    if submitted:
        now = datetime.utcnow().isoformat()
        execute(
            """
            insert into corrective_actions (
                case_id, title, owner, due_date, status, containment_action, corrective_action,
                preventive_action, verification_method, effectiveness_review_date, created_at, updated_at
            ) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (case["id"], title, owner, due_date.isoformat(), status, containment, corrective, preventive, verification, review_date.isoformat(), now, now),
        )
        audit("CAPA Created", title, case["id"])
        st.success("CAPA created.")
        st.rerun()
    actions = read_df(
        """
        select ca.id, i.case_number, ca.title, ca.owner, ca.due_date, ca.status,
        ca.corrective_action, ca.verification_method
        from corrective_actions ca join investigations i on i.id = ca.case_id order by ca.due_date
        """
    )
    st.subheader("CAPA Register")
    st.dataframe(actions, use_container_width=True, hide_index=True)


def ai_page() -> None:
    _, case = investigation_selector()
    if case is None:
        return
    evidence = read_df("select evidence_type, title, notes, file_name, created_at from evidence where case_id = ?", (case["id"],))
    result = ai_analyze(case, evidence)
    c1, c2 = st.columns([0.75, 0.25])
    with c1:
        st.subheader("AI Investigation Assistant")
        st.write(case["problem"])
    with c2:
        st.metric("Confidence", f"{result.get('confidence_level', 0)}%")
    st.markdown("#### Evidence Considered")
    st.write(result.get("evidence_considered", []))
    st.markdown("#### Findings")
    for finding in result.get("findings", []):
        st.info(finding)
    st.markdown("#### Missing Data")
    for item in result.get("missing_data", []):
        st.warning(item)
    st.markdown("#### Recommended Next Step")
    st.success(result.get("recommended_next_step", "Add evidence and continue investigation."))


def report_markdown(case: dict[str, Any], evidence: pd.DataFrame, actions: pd.DataFrame) -> str:
    action_lines = "\n".join([f"- {row.title}: {row.status}, owner {row.owner}, due {row.due_date}" for row in actions.itertuples()])
    evidence_lines = "\n".join([f"- {row.evidence_type}: {row.title}" for row in evidence.itertuples()])
    return f"""# Executive RCA Report

## {case['case_number']}: {case['title']}

Owner: {case['owner']}
Status: {case['status']}
Severity: {case['severity']}
Cost Impact: {money(case['cost_impact'])}

## Problem Statement
{case['problem']}

## Root Cause
{case['root_cause'] or 'Not yet documented.'}

## Corrective Action
{case['corrective_action'] or 'Not yet documented.'}

## Evidence
{evidence_lines or '- No evidence added yet.'}

## CAPA Register
{action_lines or '- No corrective actions created yet.'}

## Verification Expectations
Closure requires objective evidence, owner approval, effectiveness criteria, and recurrence monitoring.
"""


def reports_page() -> None:
    _, case = investigation_selector()
    if case is None:
        return
    evidence = read_df("select * from evidence where case_id = ?", (case["id"],))
    actions = read_df("select * from corrective_actions where case_id = ?", (case["id"],))
    report = report_markdown(case, evidence, actions)
    st.download_button("Download Markdown Report", report, file_name=f"{case['case_number']}_executive_report.md")
    st.markdown(report)


def admin_page() -> None:
    st.subheader("Product Readiness")
    readiness = pd.DataFrame(
        [
            ("Persistent database", "Complete in MVP", "SQLite product database is active."),
            ("Authentication and SSO", "Next", "Replace demo user with Auth0, Azure AD, or Streamlit auth layer."),
            ("Role-based access", "Next", "Map Admin, Quality Leader, Investigator, Executive, Auditor roles."),
            ("AI integration", "Partial", "Uses OpenAI when OPENAI_API_KEY is present; fallback works offline."),
            ("Audit trail", "Complete in MVP", "Investigation, evidence, and CAPA events are logged."),
            ("Enterprise integrations", "Next", "ERP/QMS/MES/email connectors need customer-specific implementation."),
            ("Commercial deployment", "Next", "Package for Streamlit Community, Streamlit in Snowflake, Azure, or AWS."),
        ],
        columns=["Capability", "Status", "Notes"],
    )
    st.dataframe(readiness, use_container_width=True, hide_index=True)
    st.subheader("Audit Log")
    logs = read_df(
        """
        select al.created_at, al.actor, al.event_type, al.description, i.case_number
        from audit_log al left join investigations i on i.id = al.case_id
        order by al.created_at desc limit 100
        """
    )
    st.dataframe(logs, use_container_width=True, hide_index=True)


def main() -> None:
    st.set_page_config(page_title=APP_NAME, layout="wide")
    init_db()
    st.title(APP_NAME)
    st.caption("Find the Cause. Fix the System. Prevent Recurrence.")
    page = sidebar()
    if page == "Executive Dashboard":
        dashboard()
    elif page == "Investigations":
        investigations_page()
    elif page == "New Investigation":
        new_investigation_page()
    elif page == "CAPA Management":
        capa_page()
    elif page == "AI Assistant":
        ai_page()
    elif page == "Reports":
        reports_page()
    elif page == "Admin & Readiness":
        admin_page()


if __name__ == "__main__":
    main()
