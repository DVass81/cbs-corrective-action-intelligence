from __future__ import annotations

import json
import os
import sqlite3
from contextlib import closing
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

APP_NAME = "CBS Corrective Action Intelligence"
DB_PATH = Path(os.getenv("CAI_DB_PATH", "data/cai_product.db"))
STATUSES = ["New", "Assigned", "Containment", "Investigation", "Root Cause Identified", "Corrective Action", "Verification", "Closed"]
SEVERITIES = ["Low", "Medium", "High", "Critical"]
TYPES = ["Quality", "Safety", "Delivery", "Downtime", "Supplier", "Engineering"]
CAPA_STATUSES = ["Open", "Assigned", "In Progress", "Completed", "Verified", "Closed"]

RCA_METHODS = [
    ("5 Whys", "Simple cause-and-effect drilling", "Evidence-backed causal chain", "Analyze"),
    ("Fishbone / Ishikawa", "Brainstorming possible causes by category", "Cause categories for deeper testing", "Analyze"),
    ("5M+1E / 6M", "Manufacturing cause categories", "Man, Machine, Method, Material, Measurement, Environment", "Analyze"),
    ("Pareto Analysis", "Prioritizing the vital few", "Ranked causes by count, cost, or impact", "Measure"),
    ("FMEA", "Risk-prioritizing failure modes", "Severity, occurrence, detection, RPN", "Analyze / Prevent"),
    ("Fault Tree Analysis", "Complex failures with logic branches", "Top event and AND/OR causal paths", "Analyze"),
    ("8D Problem Solving", "Customer-facing corrective action", "D1-D8 containment, RCA, prevention", "Full RCA"),
    ("A3 Problem Solving", "Lean management alignment", "One-page problem, analysis, countermeasure", "Full RCA"),
    ("DMAIC", "Six Sigma process improvement", "Define, Measure, Analyze, Improve, Control", "Full RCA"),
    ("PDCA / PDSA", "Iterative improvement experiments", "Plan, Do, Check/Study, Act", "Improve"),
    ("Is / Is Not", "Narrowing problem scope", "Affected vs unaffected boundaries", "Define"),
    ("Change Analysis", "Finding what changed before failure", "Change points and likely causal deltas", "Analyze"),
    ("Barrier Analysis", "Safety, quality escapes, control failures", "Missing, weak, bypassed, or failed barriers", "Analyze"),
    ("Process Mapping / SIPOC", "Understanding process handoffs", "Supplier-input-process-output-customer map", "Define"),
    ("Timeline / Event & Causal Factor Chart", "Incidents with sequence and handoffs", "Event sequence and causal factors", "Analyze"),
    ("Control Chart / Run Chart", "Variation and stability", "Common-cause vs special-cause signals", "Measure"),
    ("Scatter / Correlation", "Testing variable relationships", "Candidate input-output relationship", "Analyze"),
    ("Check Sheet / Stratification", "Collecting and splitting occurrence data", "Defects by line, shift, supplier, time", "Measure"),
    ("Current Reality Tree", "Systems thinking", "Core conflict or policy constraint", "Analyze"),
    ("Bowtie Analysis", "Risk controls before and after event", "Threats, barriers, event, recovery controls", "Prevent"),
]

DEMO = [
    ("CAI-2026-001", "Incorrect Copper Material Ordered", "Purchasing", "Raw material planning", "Copper bus bar", "Internal production", "Midwest Metals", "2026-05-08", "Maria Chen", "Corrective Action", "High", "Supplier", 84200, 86, 1, "C110 copper was ordered instead of C101 copper for a high-conductivity assembly, causing production hold and expedited replacement material.", "ERP item master allowed substitute material without engineering approval gate.", "Lock controlled alloy fields and require engineering approval for substitutions.", "2026-06-14"),
    ("CAI-2026-002", "Customer Complaint on Commutator Quality", "Quality", "Final inspection", "Motor commutator", "Northline Drives", "Internal machining", "2026-05-12", "Andre Miller", "Verification", "Critical", "Quality", 126000, 91, 0, "Customer reported elevated brush wear traced to commutator surface finish above specification on two shipped lots.", "Grinding wheel dressing interval was extended without capability validation.", "Restore controlled dressing interval and add SPC trigger for surface finish drift.", "2026-06-10"),
    ("CAI-2026-003", "Machine Downtime Event", "Maintenance", "CNC turning cell", "Shaft assembly", "Internal assembly", "OEM service", "2026-05-18", "Priya Shah", "Investigation", "High", "Downtime", 48900, 73, 1, "CNC lathe L-14 stopped repeatedly during second shift due to servo overload alarms, creating 9.5 hours of unplanned downtime.", "Likely lubrication restriction and missing TPM inspection point.", "Add lubrication flow check to weekly TPM and replace restricted metering valve.", "2026-06-08"),
]


def connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def read_df(sql: str, params: tuple[Any, ...] = ()) -> pd.DataFrame:
    with closing(connect()) as conn:
        return pd.read_sql_query(sql, conn, params=params)


def read_one(sql: str, params: tuple[Any, ...] = ()) -> dict[str, Any] | None:
    with closing(connect()) as conn:
        row = conn.execute(sql, params).fetchone()
        return dict(row) if row else None


def execute(sql: str, params: tuple[Any, ...] = ()) -> None:
    with closing(connect()) as conn:
        conn.execute(sql, params)
        conn.commit()


def audit(event_type: str, description: str, case_id: int | None = None) -> None:
    execute("insert into audit_log (case_id,event_type,description,actor,created_at) values (?,?,?,?,?)", (case_id, event_type, description, st.session_state.get("actor", "Demo User"), datetime.utcnow().isoformat()))


def init_db() -> None:
    with closing(connect()) as conn:
        conn.executescript("""
        create table if not exists investigations (id integer primary key autoincrement, case_number text unique, title text, department text, process text, product text, customer text, supplier text, detection_date text, owner text, status text, severity text, case_type text, cost_impact real, rca_score integer, repeat_issue integer, problem text, root_cause text default '', corrective_action text default '', due_date text, created_at text, updated_at text);
        create table if not exists corrective_actions (id integer primary key autoincrement, case_id integer, title text, owner text, due_date text, status text, containment_action text default '', corrective_action text default '', preventive_action text default '', verification_method text default '', effectiveness_review_date text, created_at text, updated_at text);
        create table if not exists evidence (id integer primary key autoincrement, case_id integer, evidence_type text, title text, notes text default '', file_name text default '', created_at text);
        create table if not exists audit_log (id integer primary key autoincrement, case_id integer, event_type text, description text, actor text, created_at text);
        """)
        if conn.execute("select count(*) from investigations").fetchone()[0] == 0:
            now = datetime.utcnow().isoformat()
            for row in DEMO:
                conn.execute("""
                insert into investigations (case_number,title,department,process,product,customer,supplier,detection_date,owner,status,severity,case_type,cost_impact,rca_score,repeat_issue,problem,root_cause,corrective_action,due_date,created_at,updated_at)
                values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                """, (*row, now, now))
            for i, row in enumerate(conn.execute("select id,case_number,owner,corrective_action,due_date from investigations"), start=1):
                conn.execute("""
                insert into corrective_actions (case_id,title,owner,due_date,status,containment_action,corrective_action,preventive_action,verification_method,effectiveness_review_date,created_at,updated_at)
                values (?,?,?,?,?,?,?,?,?,?,?,?)
                """, (row["id"], f"CAPA for {row['case_number']}", row["owner"], row["due_date"], CAPA_STATUSES[i-1], "Protect customer demand and quarantine suspect output.", row["corrective_action"], "Update control plan, train owners, and monitor recurrence.", "30-day recurrence check with layered process audit evidence.", "2026-07-15", now, now))
            conn.commit()


def money(v: float | int) -> str:
    return f"${float(v):,.0f}"


def case_selector() -> tuple[pd.DataFrame, dict[str, Any] | None]:
    cases = read_df("select * from investigations order by detection_date desc,id desc")
    if cases.empty:
        st.info("No investigations yet.")
        return cases, None
    labels = [f"{r.case_number} - {r.title}" for r in cases.itertuples()]
    selected = st.selectbox("Investigation", labels)
    return cases, read_one("select * from investigations where case_number=?", (selected.split(" - ", 1)[0],))


def rca_playbook(case: dict[str, Any], evidence: pd.DataFrame) -> dict[str, Any]:
    process = case.get("process") or "the affected process"
    product = case.get("product") or "the affected product"
    root = case.get("root_cause") or "the true system cause is not yet proven"
    corrective = case.get("corrective_action") or "a verified system control has not yet been selected"
    why = [
        ("Why did the problem occur?", case.get("problem", "")),
        ("Why did the process allow it?", f"The control point in {process} did not detect or prevent the failure."),
        ("Why was the control ineffective?", f"The standard work, approval gate, or verification method did not force objective confirmation for {product}."),
        ("Why was the system not updated?", "Lessons learned were not converted into a governed control plan, audit item, or error-proofing requirement."),
        ("What system cause must be fixed?", root),
    ]
    categories = [
        ("Manpower", "Training or role clarity did not make the required check unavoidable.", "Training matrix, interview, responsibility."),
        ("Machine", "Equipment, fixture, software, or ERP setting allowed the defect path.", "Machine logs, ERP settings, fixture condition."),
        ("Method", "Standard work or approval workflow missed a verification step.", "Work instruction, control plan, process map."),
        ("Material", "Material, supplier, revision, or lot control did not match specification.", "COC, receiving records, traceability."),
        ("Measurement", "Inspection frequency, gage method, or criteria did not catch the issue.", "Inspection records, MSA, SPC data."),
        ("Environment", "Shift, schedule, layout, workload, or visual conditions increased risk.", "Shift records, workload, layout photos."),
    ]
    strategy = {
        "Quality": ["Poka-yoke the defect path", "Add SPC or go/no-go verification", "Update the control plan"],
        "Safety": ["Engineer out exposure", "Add interlocked guarding", "Add layered safety audit"],
        "Delivery": ["Install visual flow control", "Add escalation trigger", "Create promise-date confirmation"],
        "Downtime": ["Add TPM check", "Add condition-based trigger", "Standardize response plan"],
        "Supplier": ["Tighten supplier approval gate", "Add incoming verification trigger", "Create supplier corrective action review"],
        "Engineering": ["Move to controlled digital work instructions", "Add obsolete-document removal audit", "Tie ECO release to point-of-use control"],
    }.get(case.get("case_type"), ["Poka-yoke", "Standard work", "Layered audit"])
    actions = [
        {"title": f"Error-proof {process}", "containment_action": "Protect the customer and quarantine suspect output until risk is bounded.", "corrective_action": f"Implement a poka-yoke or hard approval gate so {corrective.lower()}.", "preventive_action": "Update the control plan and standard work so the control is owned, trained, and audited.", "verification_method": "Verify with objective evidence from the next 30 days of production or transactions."},
        {"title": "Convert lesson learned into layered process audit", "containment_action": "Review active jobs, lots, or orders for the same failure path.", "corrective_action": "Add the failure mode to a layered process audit with owner, frequency, and escalation rules.", "preventive_action": "Review repeat issues monthly and add recurrence triggers to daily management.", "verification_method": "Three consecutive audit cycles with no recurrence and documented leader signoff."},
        {"title": "Strengthen measurement and effectiveness criteria", "containment_action": "Confirm current checks catch the issue before release.", "corrective_action": "Define measurable effectiveness criteria, sample size, and closure evidence before CAPA closure.", "preventive_action": "Add the measurement method to training, onboarding, and future change reviews.", "verification_method": "Evidence package includes sample results, owner approval, and recurrence check."},
    ]
    return {"five_why": why, "five_m_one_e": categories, "lean_strategies": strategy, "recommended_actions": actions, "evidence_count": len(evidence)}


def capa_quality_feedback(text: str) -> tuple[str, list[str]]:
    lower = text.lower()
    if any(x in lower for x in ["retrain", "train", "remind", "coach", "discipline", "be careful", "pay attention"]):
        return "Weak", ["Add poka-yoke or interlock.", "Update standard work and control plan.", "Add layered audit and measurable verification."]
    if any(x in lower for x in ["poka", "interlock", "control plan", "audit", "spc", "go/no-go", "standard work", "verification"]):
        return "Strong", ["This changes the process or control system. Confirm owner, due date, and recurrence check."]
    return "Needs Detail", ["Clarify the system control change.", "Define verification evidence.", "Add owner and recurrence check."]


def closure_score(case: dict[str, Any], evidence: pd.DataFrame, actions: pd.DataFrame) -> tuple[int, list[dict[str, Any]]]:
    checks = [
        {"Gate": "Problem statement", "Pass": bool(case.get("problem")), "Why It Matters": "The team must agree on the actual problem."},
        {"Gate": "Evidence attached", "Pass": not evidence.empty, "Why It Matters": "Closure needs objective evidence."},
        {"Gate": "Root cause documented", "Pass": bool(case.get("root_cause")), "Why It Matters": "CAPA must target a verified system cause."},
        {"Gate": "Corrective action exists", "Pass": bool(case.get("corrective_action")) or not actions.empty, "Why It Matters": "The system change must be explicit."},
        {"Gate": "CAPA owner assigned", "Pass": (not actions.empty and actions["owner"].fillna("").str.len().gt(0).all()), "Why It Matters": "CAPA needs accountable ownership."},
        {"Gate": "Verification method", "Pass": (not actions.empty and actions["verification_method"].fillna("").str.len().gt(0).all()), "Why It Matters": "Effectiveness must be proven."},
        {"Gate": "No weak CAPA language", "Pass": not any(capa_quality_feedback(str(x))[0] == "Weak" for x in actions["corrective_action"].tolist()) if not actions.empty else False, "Why It Matters": "Training-only fixes rarely change the system."},
    ]
    return round(100 * sum(1 for x in checks if x["Pass"]) / len(checks)), checks


def method_recommendations(case: dict[str, Any]) -> pd.DataFrame:
    preferred = {
        "Quality": ["5 Whys", "Fishbone / Ishikawa", "5M+1E / 6M", "FMEA", "Control Chart / Run Chart", "Pareto Analysis"],
        "Safety": ["Barrier Analysis", "Bowtie Analysis", "Timeline / Event & Causal Factor Chart", "5 Whys", "Fishbone / Ishikawa"],
        "Delivery": ["Process Mapping / SIPOC", "Pareto Analysis", "Is / Is Not", "Change Analysis", "DMAIC"],
        "Downtime": ["Fault Tree Analysis", "FMEA", "Timeline / Event & Causal Factor Chart", "5 Whys"],
        "Supplier": ["8D Problem Solving", "Pareto Analysis", "FMEA", "Change Analysis", "Is / Is Not"],
        "Engineering": ["Change Analysis", "Process Mapping / SIPOC", "A3 Problem Solving", "Barrier Analysis", "5 Whys"],
    }.get(case.get("case_type"), ["5 Whys", "Fishbone / Ishikawa", "Pareto Analysis"])
    rows = []
    for m, best, output, phase in RCA_METHODS:
        rows.append({"Method": m, "Best For": best, "Output": output, "Phase": phase, "Recommended": "Yes" if m in preferred else "Optional"})
    return pd.DataFrame(rows)


def create_generated_capa(case: dict[str, Any], action: dict[str, str]) -> bool:
    if read_one("select id from corrective_actions where case_id=? and title=?", (case["id"], action["title"])):
        return False
    now = datetime.utcnow().isoformat()
    execute("""
    insert into corrective_actions (case_id,title,owner,due_date,status,containment_action,corrective_action,preventive_action,verification_method,effectiveness_review_date,created_at,updated_at)
    values (?,?,?,?,?,?,?,?,?,?,?,?)
    """, (case["id"], action["title"], case.get("owner") or "Unassigned", (date.today()+timedelta(days=30)).isoformat(), "Assigned", action["containment_action"], action["corrective_action"], action["preventive_action"], action["verification_method"], (date.today()+timedelta(days=60)).isoformat(), now, now))
    audit("AI CAPA Created", action["title"], case["id"])
    return True


def rca_map(case: dict[str, Any], score: int) -> go.Figure:
    labels = ["Problem", "Evidence", "RCA Methods", "Root Cause", "CAPA", "Verification"]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=list(range(6)), y=[1]*6, mode="lines", line=dict(color="#334155", width=6), hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=list(range(6)), y=[1]*6, mode="markers+text", marker=dict(size=34, color=["#ef4444", "#f59e0b", "#28a8ff", "#8b5cf6", "#22c55e", "#14b8a6"], line=dict(color="white", width=2)), text=labels, textposition="bottom center", hovertext=[case.get("problem"), "Evidence records", "Method library", case.get("root_cause") or "Not verified", case.get("corrective_action") or "Generated CAPA", f"Closure {score}%"], hoverinfo="text"))
    fig.update_layout(height=260, margin=dict(l=20,r=20,t=20,b=40), xaxis=dict(visible=False), yaxis=dict(visible=False), showlegend=False)
    return fig


def risk_badges(case: dict[str, Any], score: int) -> None:
    sev = {"Low":"#22c55e","Medium":"#f59e0b","High":"#f97316","Critical":"#ef4444"}.get(case.get("severity"), "#64748b")
    st.markdown(f"""
    <div style='display:flex;gap:10px;flex-wrap:wrap;margin-bottom:1rem;'>
      <span style='background:{sev};color:white;padding:6px 10px;border-radius:999px;'>Severity: {case.get('severity')}</span>
      <span style='background:#28a8ff;color:white;padding:6px 10px;border-radius:999px;'>Status: {case.get('status')}</span>
      <span style='background:{'#ef4444' if int(case.get('repeat_issue') or 0) else '#22c55e'};color:white;padding:6px 10px;border-radius:999px;'>Repeat: {'Yes' if int(case.get('repeat_issue') or 0) else 'No'}</span>
      <span style='background:#334155;color:white;padding:6px 10px;border-radius:999px;'>Closure readiness: {score}%</span>
    </div>""", unsafe_allow_html=True)


def ai_analyze(case: dict[str, Any], evidence: pd.DataFrame) -> dict[str, Any]:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        missing = []
        if evidence.empty: missing.append("Objective evidence has not been attached yet.")
        if int(case.get("repeat_issue") or 0): missing.append("Prior occurrence search should be documented.")
        return {"evidence_considered": evidence["title"].tolist() if not evidence.empty else ["Problem statement", "Case metadata"], "findings": ["Treat this as a system-control problem, not a blame exercise.", "Use RCA Toolbox outputs to generate verified CAPAs."], "missing_data": missing or ["Confirm effectiveness criteria before closure."], "recommended_next_step": "Use RCA Toolbox to validate causes and create generated CAPA.", "confidence_level": max(35, min(95, int(case.get("rca_score") or 50)))}
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        prompt = {"case": case, "evidence": evidence.to_dict(orient="records"), "instruction": "Return compact JSON with evidence_considered, findings, missing_data, recommended_next_step, confidence_level. Do not include hidden reasoning."}
        return json.loads(client.responses.create(model=os.getenv("CAI_OPENAI_MODEL", "gpt-4.1-mini"), input=json.dumps(prompt)).output_text.strip())
    except Exception as exc:
        return {"evidence_considered": ["Problem statement"], "findings": [f"OpenAI unavailable: {exc}"], "missing_data": ["Use offline RCA tools."], "recommended_next_step": "Use RCA Toolbox.", "confidence_level": 50}


def sidebar() -> str:
    st.sidebar.title("CBS CAI")
    st.sidebar.caption("Corrective Action Intelligence")
    if "actor" not in st.session_state: st.session_state["actor"] = "Demo User"
    st.sidebar.text_input("Signed in as", key="actor")
    return st.sidebar.radio("Workspace", ["Executive Dashboard", "Guided Investigation", "Investigation Workspace", "Investigations", "New Investigation", "RCA Toolbox", "CAPA Management", "AI Assistant", "Reports", "Admin & Readiness"])


def dashboard() -> None:
    cases = read_df("select * from investigations order by detection_date desc")
    actions = read_df("select * from corrective_actions")
    open_cases = cases[cases["status"] != "Closed"]
    overdue = actions[(actions["status"] != "Closed") & (actions["due_date"] < date.today().isoformat())] if not actions.empty else actions
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Open Investigations", len(open_cases)); c2.metric("Cost of Poor Quality", money(cases["cost_impact"].sum())); c3.metric("Average RCA Score", int(cases["rca_score"].mean()) if not cases.empty else 0); c4.metric("Overdue CAPAs", len(overdue))
    left,right = st.columns([1.2,.8])
    with left:
        st.plotly_chart(px.bar(cases.groupby("case_type", as_index=False).agg(count=("id","count"), cost=("cost_impact","sum")), x="case_type", y="count", color="cost", title="Issue Pareto"), use_container_width=True)
    with right:
        st.plotly_chart(px.pie(cases.groupby("status", as_index=False).size(), names="status", values="size", title="Status Mix"), use_container_width=True)
    st.subheader("Risk Queue"); st.dataframe(cases[["case_number","title","department","owner","status","severity","due_date","cost_impact","rca_score"]], use_container_width=True, hide_index=True)


def guided_investigation() -> None:
    st.subheader("Guided Investigation Interview")
    prompts = [("What failed or went wrong?", "failure"), ("Where was it detected?", "where"), ("When was it first detected?", "when"), ("Who found it or was affected?", "who"), ("What changed recently?", "change"), ("What evidence is available?", "evidence"), ("What containment happened?", "containment")]
    with st.form("guided"):
        answers = {k: st.text_area(q, height=70) for q,k in prompts}
        if st.form_submit_button("Generate Investigation Draft"):
            st.session_state["guided_problem"] = f"{answers['failure']} was detected at {answers['where']} on {answers['when']}. It affected {answers['who']}. Recent change: {answers['change']}. Evidence: {answers['evidence']}. Containment: {answers['containment']}."
    draft = st.text_area("AI Draft Problem Statement", value=st.session_state.get("guided_problem", ""), height=130)
    c1,c2,c3 = st.columns(3); title=c1.text_input("Case title", "Guided RCA Investigation"); owner=c2.text_input("Owner", st.session_state.get("actor","Demo User")); case_type=c3.selectbox("Issue type", TYPES)
    dept=st.text_input("Department", "Quality"); process=st.text_input("Process")
    if st.button("Create Investigation From Draft"):
        now=datetime.utcnow().isoformat(); number=f"CAI-{date.today().year}-{read_df('select id from investigations').shape[0]+1:03d}"
        execute("""insert into investigations (case_number,title,department,process,product,customer,supplier,detection_date,owner,status,severity,case_type,cost_impact,rca_score,repeat_issue,problem,root_cause,corrective_action,due_date,created_at,updated_at) values (?,?,?,?, '', '', '', ?, ?, 'New', 'Medium', ?, 0, 50, 0, ?, '', '', ?, ?, ?)""", (number,title,dept,process,date.today().isoformat(),owner,case_type,draft,(date.today()+timedelta(days=30)).isoformat(),now,now))
        st.success(f"{number} created.")


def workspace() -> None:
    _,case=case_selector();
    if not case: return
    evidence=read_df("select * from evidence where case_id=?",(case["id"],)); actions=read_df("select * from corrective_actions where case_id=?",(case["id"],)); score,checks=closure_score(case,evidence,actions)
    risk_badges(case,score); st.plotly_chart(rca_map(case,score), use_container_width=True)
    s,m,a,c=st.tabs(["Case Summary","RCA Methods","CAPA Quality","Closure Gates"])
    with s: st.write(case["problem"]); st.dataframe(evidence if not evidence.empty else pd.DataFrame(columns=["evidence_type","title","notes"]), use_container_width=True, hide_index=True)
    with m: st.dataframe(method_recommendations(case), use_container_width=True, hide_index=True)
    with a:
        if actions.empty: st.info("No CAPAs yet. Use AI generated actions.")
        for row in actions.itertuples():
            rating,feedback=capa_quality_feedback(row.corrective_action); st.write(f"**{row.title}** - {rating}"); [st.caption(x) for x in feedback]
    with c: st.metric("Ready to Close", f"{score}%"); st.dataframe(pd.DataFrame(checks), use_container_width=True, hide_index=True)


def investigations() -> None:
    cases,case=case_selector();
    if not case: return
    st.dataframe(cases[["case_number","title","department","owner","status","severity","due_date","cost_impact","rca_score"]], use_container_width=True, hide_index=True)
    with st.form("update_case"):
        c1,c2,c3=st.columns(3); status=c1.selectbox("Status", STATUSES, index=STATUSES.index(case["status"])); owner=c2.text_input("Owner", case["owner"] or ""); due=c3.date_input("Due date", date.fromisoformat(case["due_date"]) if case["due_date"] else date.today())
        problem=st.text_area("Problem", case["problem"], height=100); root=st.text_area("Root cause", case["root_cause"] or ""); corrective=st.text_area("Corrective action", case["corrective_action"] or ""); score=st.slider("RCA score",0,100,int(case["rca_score"] or 50)); save=st.form_submit_button("Save")
    if save:
        execute("update investigations set status=?,owner=?,due_date=?,problem=?,root_cause=?,corrective_action=?,rca_score=?,updated_at=? where id=?",(status,owner,due.isoformat(),problem,root,corrective,score,datetime.utcnow().isoformat(),case["id"])); st.success("Saved"); st.rerun()
    evidence_widget(case)


def evidence_widget(case: dict[str, Any]) -> None:
    st.subheader("Evidence"); evidence=read_df("select * from evidence where case_id=? order by created_at desc",(case["id"],))
    if not evidence.empty: st.dataframe(evidence[["evidence_type","title","notes","file_name","created_at"]], use_container_width=True, hide_index=True)
    with st.form(f"ev_{case['id']}"):
        c1,c2=st.columns(2); et=c1.selectbox("Evidence type", ["Photo","ERP Record","Inspection Record","Interview","Document","Other"]); title=c2.text_input("Title"); notes=st.text_area("Notes"); up=st.file_uploader("Attach file metadata")
        if st.form_submit_button("Add Evidence"):
            execute("insert into evidence (case_id,evidence_type,title,notes,file_name,created_at) values (?,?,?,?,?,?)",(case["id"],et,title,notes,up.name if up else "",datetime.utcnow().isoformat())); st.rerun()


def new_investigation() -> None:
    st.subheader("Create Investigation")
    number=f"CAI-{date.today().year}-{read_df('select id from investigations').shape[0]+1:03d}"
    with st.form("new"):
        c1,c2,c3=st.columns(3); num=c1.text_input("Case number", number); title=c2.text_input("Title"); owner=c3.text_input("Owner")
        c4,c5,c6=st.columns(3); dept=c4.text_input("Department"); sev=c5.selectbox("Severity",SEVERITIES,index=2); typ=c6.selectbox("Type",TYPES)
        process=st.text_input("Process"); product=st.text_input("Product"); customer=st.text_input("Customer"); supplier=st.text_input("Supplier"); detected=st.date_input("Detection date",date.today()); due=st.date_input("Due date",date.today()); cost=st.number_input("Cost impact",0.0,step=1000.0); repeat=st.checkbox("Repeat issue"); problem=st.text_area("Problem",height=120)
        if st.form_submit_button("Create"):
            now=datetime.utcnow().isoformat(); execute("""insert into investigations (case_number,title,department,process,product,customer,supplier,detection_date,owner,status,severity,case_type,cost_impact,rca_score,repeat_issue,problem,root_cause,corrective_action,due_date,created_at,updated_at) values (?,?,?,?,?,?,?,?,?,'New',?,?,?,?,?,?,'','',?,?,?)""",(num,title,dept,process,product,customer,supplier,detected.isoformat(),owner,sev,typ,cost,50,1 if repeat else 0,problem,due.isoformat(),now,now)); st.success(f"{num} created")


def action_blocks(case: dict[str, Any], prefix: str) -> None:
    playbook=rca_playbook(case, read_df("select * from evidence where case_id=?",(case["id"],)))
    for i,act in enumerate(playbook["recommended_actions"],1):
        with st.expander(act["title"], expanded=i==1):
            st.write(f"Containment: {act['containment_action']}"); st.write(f"Corrective action: {act['corrective_action']}"); st.write(f"Preventive action: {act['preventive_action']}"); st.write(f"Verification: {act['verification_method']}")
            if st.button("Create CAPA from this recommendation", key=f"{prefix}_{case['id']}_{i}"):
                st.success("Generated CAPA created." if create_generated_capa(case,act) else "That generated CAPA already exists."); st.rerun()


def capa_page() -> None:
    _,case=case_selector();
    if not case: return
    st.subheader("AI Suggested Corrective Actions"); action_blocks(case,"capa")
    with st.form("manual_capa"):
        st.subheader("Manual CAPA Entry"); title=st.text_input("Title",f"Corrective action for {case['case_number']}"); c1,c2,c3=st.columns(3); owner=c1.text_input("Owner",case["owner"] or ""); due=c2.date_input("Due date",date.today()); status=c3.selectbox("Status",CAPA_STATUSES); cont=st.text_area("Containment"); corr=st.text_area("Corrective",case["corrective_action"] or ""); prev=st.text_area("Preventive"); ver=st.text_area("Verification"); review=st.date_input("Review date",date.today())
        if st.form_submit_button("Create CAPA"):
            now=datetime.utcnow().isoformat(); execute("insert into corrective_actions (case_id,title,owner,due_date,status,containment_action,corrective_action,preventive_action,verification_method,effectiveness_review_date,created_at,updated_at) values (?,?,?,?,?,?,?,?,?,?,?,?)",(case["id"],title,owner,due.isoformat(),status,cont,corr,prev,ver,review.isoformat(),now,now)); st.rerun()
    st.dataframe(read_df("select ca.id,i.case_number,ca.title,ca.owner,ca.due_date,ca.status,ca.corrective_action,ca.verification_method from corrective_actions ca join investigations i on i.id=ca.case_id order by ca.due_date"), use_container_width=True, hide_index=True)


def toolbox() -> None:
    _,case=case_selector();
    if not case: return
    evidence=read_df("select * from evidence where case_id=?",(case["id"],)); playbook=rca_playbook(case,evidence)
    tabs=st.tabs(["Method Library","5 Why","5M+1E","Visual Tools","Lean Strategy","Generated CAPAs"])
    with tabs[0]: st.dataframe(method_recommendations(case), use_container_width=True, hide_index=True)
    with tabs[1]: st.dataframe(pd.DataFrame(playbook["five_why"], columns=["Question","AI Draft"]), use_container_width=True, hide_index=True)
    with tabs[2]:
        cats=playbook["five_m_one_e"]
        for start in range(0,len(cats),3):
            cols=st.columns(3)
            for col,item in zip(cols,cats[start:start+3]):
                col.markdown(f"<div style='border:1px solid #334155;border-radius:10px;padding:14px;min-height:165px;background:#111827;'><h4 style='color:#72ddff'>{item[0]}</h4><p>{item[1]}</p><small>Evidence: {item[2]}</small></div>", unsafe_allow_html=True)
    with tabs[3]:
        actions=read_df("select * from corrective_actions where case_id=?",(case["id"],)); score,_=closure_score(case,evidence,actions); st.plotly_chart(rca_map(case,score), use_container_width=True)
        fmea=pd.DataFrame([{"Failure Mode":case["title"],"Effect":case["problem"][:90],"Severity":8 if case["severity"] in ["High","Critical"] else 5,"Occurrence":5 if int(case["repeat_issue"] or 0) else 3,"Detection":5}]); fmea["RPN"]=fmea["Severity"]*fmea["Occurrence"]*fmea["Detection"]; st.dataframe(fmea, use_container_width=True, hide_index=True)
        st.plotly_chart(px.bar(pd.DataFrame([("Process control",31),("Supplier",24),("Training",18),("Maintenance",14),("Engineering",9)], columns=["Cause","Impact"]), x="Cause", y="Impact", title="Pareto Starter"), use_container_width=True)
        st.write("Fault tree starter: Top event -> control escaped OR process drifted OR specification unclear.")
    with tabs[4]: [st.success(x) for x in playbook["lean_strategies"]]; st.write("Contain first, prove the system cause, error-proof the failure path, update standard work/control plan, train owners, then verify recurrence evidence.")
    with tabs[5]: action_blocks(case,"toolbox")


def ai_page() -> None:
    _,case=case_selector();
    if not case: return
    evidence=read_df("select * from evidence where case_id=?",(case["id"],)); result=ai_analyze(case,evidence)
    c1,c2=st.columns([.75,.25]); c1.subheader("AI Investigation Assistant"); c1.write(case["problem"]); c2.metric("Confidence", f"{result.get('confidence_level',0)}%")
    st.markdown("#### Evidence Considered"); st.write(result.get("evidence_considered",[])); st.markdown("#### Findings"); [st.info(x) for x in result.get("findings",[])]; st.markdown("#### Missing Data"); [st.warning(x) for x in result.get("missing_data",[])]; st.success(result.get("recommended_next_step","Use RCA Toolbox.")); st.markdown("#### Generated Corrective Actions"); action_blocks(case,"ai")


def report_text(case: dict[str, Any], evidence: pd.DataFrame, actions: pd.DataFrame) -> str:
    playbook=rca_playbook(case,evidence); ev="\n".join([f"- {r.evidence_type}: {r.title}" for r in evidence.itertuples()]) or "- No evidence added yet."; acts="\n".join([f"- {r.title}: {r.status}, owner {r.owner}, due {r.due_date}" for r in actions.itertuples()]) or "- No corrective actions created yet."; why="\n".join([f"- {q} {a}" for q,a in playbook["five_why"]]); methods="\n".join([f"- {r['Method']}: {r['Output']}" for r in method_recommendations(case).to_dict(orient="records") if r["Recommended"]=="Yes"]); lean="\n".join([f"- {x}" for x in playbook["lean_strategies"]])
    return f"""# Executive RCA Report\n\n## {case['case_number']}: {case['title']}\nOwner: {case['owner']}\nStatus: {case['status']}\nSeverity: {case['severity']}\nCost Impact: {money(case['cost_impact'])}\n\n## Problem Statement\n{case['problem']}\n\n## Root Cause\n{case['root_cause'] or 'Not yet documented.'}\n\n## Evidence\n{ev}\n\n## 5 Why Analysis\n{why}\n\n## RCA Methods Applied\n{methods}\n\n## Lean Strategy\n{lean}\n\n## CAPA Register\n{acts}\n\n## Verification Expectations\nClosure requires objective evidence, owner approval, effectiveness criteria, and recurrence monitoring.\n"""


def reports() -> None:
    _,case=case_selector();
    if not case: return
    evidence=read_df("select * from evidence where case_id=?",(case["id"],)); actions=read_df("select * from corrective_actions where case_id=?",(case["id"],)); report=report_text(case,evidence,actions); st.download_button("Download Markdown Report", report, file_name=f"{case['case_number']}_executive_report.md"); st.markdown(report)


def admin() -> None:
    rows=[("Persistent database","Complete","SQLite product database is active."),("Guided workflow","Complete","Interview prompts create draft investigations."),("Workspace","Complete","RCA map, methods, CAPA quality, closure gates."),("RCA method library","Complete","5 Why, fishbone, 5M+1E, Pareto, FMEA, fault tree, 8D, A3, DMAIC, PDCA, and more."),("Authentication and SSO","Next","Add Auth0, Azure AD, or Streamlit auth."),("Integrations","Next","ERP/QMS/MES/email connectors.")]
    st.dataframe(pd.DataFrame(rows,columns=["Capability","Status","Notes"]), use_container_width=True, hide_index=True); st.subheader("Audit Log"); st.dataframe(read_df("select al.created_at,al.actor,al.event_type,al.description,i.case_number from audit_log al left join investigations i on i.id=al.case_id order by al.created_at desc limit 100"), use_container_width=True, hide_index=True)


def main() -> None:
    st.set_page_config(page_title=APP_NAME, layout="wide")
    init_db(); st.title(APP_NAME); st.caption("Find the Cause. Fix the System. Prevent Recurrence.")
    page=sidebar()
    if page=="Executive Dashboard": dashboard()
    elif page=="Guided Investigation": guided_investigation()
    elif page=="Investigation Workspace": workspace()
    elif page=="Investigations": investigations()
    elif page=="New Investigation": new_investigation()
    elif page=="RCA Toolbox": toolbox()
    elif page=="CAPA Management": capa_page()
    elif page=="AI Assistant": ai_page()
    elif page=="Reports": reports()
    elif page=="Admin & Readiness": admin()

if __name__ == "__main__":
    main()
