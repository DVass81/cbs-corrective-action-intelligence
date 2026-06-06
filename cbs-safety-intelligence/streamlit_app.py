import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="CBS Safety Intelligence",
    page_icon="CBS",
    layout="wide",
    initial_sidebar_state="expanded",
)


DEPARTMENTS = pd.DataFrame(
    [
        {"Department": "Machine Shop", "Score": 86, "Risk": 71, "Hazards": 12, "Shift": "A", "Training": 91},
        {"Department": "Assembly", "Score": 92, "Risk": 42, "Hazards": 5, "Shift": "B", "Training": 96},
        {"Department": "Shipping", "Score": 74, "Risk": 83, "Hazards": 16, "Shift": "A", "Training": 82},
        {"Department": "Maintenance", "Score": 79, "Risk": 77, "Hazards": 9, "Shift": "C", "Training": 84},
        {"Department": "Winding", "Score": 88, "Risk": 49, "Hazards": 7, "Shift": "B", "Training": 89},
        {"Department": "Quality", "Score": 95, "Risk": 25, "Hazards": 2, "Shift": "A", "Training": 98},
    ]
)

KPI_ROWS = [
    ("Safety Score", "84/100", "On track", "good"),
    ("Open Hazards", "51", "12 high risk", "warn"),
    ("Near Misses", "18", "+5 from last month", "neutral"),
    ("Overdue Actions", "7", "3 escalated", "critical"),
    ("Training Compliance", "91%", "Forklift due soon", "good"),
    ("JHA Completion", "76%", "8 jobs missing", "warn"),
    ("Incidents This Month", "2", "1 recordable", "critical"),
    ("Risk Trend", "-11%", "30-day rolling", "good"),
]

ACTIONS = pd.DataFrame(
    [
        {"ID": "CA-1048", "Action": "Install fixed guard on press brake #4", "Owner": "M. Rivera", "Due": "Today", "Priority": "Critical", "Status": "Overdue"},
        {"ID": "CA-1051", "Action": "Retrain Shipping A shift on pedestrian aisles", "Owner": "T. Lewis", "Due": "Tomorrow", "Priority": "High", "Status": "Open"},
        {"ID": "CA-1057", "Action": "Verify new eyewash station signage", "Owner": "S. Patel", "Due": "Jun 10", "Priority": "Medium", "Status": "Verification"},
        {"ID": "CA-1060", "Action": "Close JHA approval for coil winding setup", "Owner": "A. Chen", "Due": "Jun 12", "Priority": "Medium", "Status": "Open"},
    ]
)

TRAINING = pd.DataFrame(
    [
        {"Training": "Forklift", "Complete": 88, "Overdue": 4, "Expires": "14 days"},
        {"Training": "Crane", "Complete": 94, "Overdue": 1, "Expires": "31 days"},
        {"Training": "Lockout/Tagout", "Complete": 86, "Overdue": 6, "Expires": "8 days"},
        {"Training": "HazCom", "Complete": 97, "Overdue": 0, "Expires": "72 days"},
        {"Training": "PPE", "Complete": 92, "Overdue": 2, "Expires": "21 days"},
        {"Training": "Bloodborne Pathogens", "Complete": 81, "Overdue": 8, "Expires": "5 days"},
    ]
)


def inject_css() -> None:
    st.markdown(
        """
        <style>
        :root { --navy:#08111f; --steel:#5ea1d8; --green:#34d399; --amber:#f5b84b; --red:#f16063; --muted:#8da0b8; }
        .stApp { background: radial-gradient(circle at top left, rgba(94,161,216,.2), transparent 34rem), var(--navy); color:#edf4ff; }
        [data-testid="stSidebar"] { background: rgba(6,14,26,.92); border-right:1px solid rgba(255,255,255,.1); }
        h1, h2, h3 { letter-spacing:0 !important; }
        .hero { padding:26px; border-radius:18px; border:1px solid rgba(255,255,255,.1); background:linear-gradient(180deg, rgba(255,255,255,.09), rgba(255,255,255,.045)); box-shadow:0 24px 70px rgba(0,0,0,.28); }
        .hero h1 { font-size:clamp(2rem,5vw,4rem); line-height:1; margin:0 0 .6rem; }
        .subtle { color:var(--muted); }
        .chip { display:inline-flex; align-items:center; min-height:28px; padding:0 10px; margin:4px 6px 4px 0; border-radius:999px; font-size:12px; font-weight:800; background:rgba(255,255,255,.1); border:1px solid rgba(255,255,255,.1); }
        .good { background:var(--green); color:#063820; } .warn { background:var(--amber); color:#3e2700; } .critical { background:var(--red); color:#40070a; }
        .kpi, .feed, .card { padding:18px; border-radius:16px; border:1px solid rgba(255,255,255,.1); background:rgba(255,255,255,.07); }
        .kpi { min-height:128px; } .kpi strong { display:block; font-size:2.15rem; line-height:1; margin:.5rem 0; }
        .heat { padding:16px; border-radius:14px; min-height:112px; border:1px solid rgba(255,255,255,.1); }
        .heat strong, .heat span, .heat small { display:block; } .heat span { font-size:1.6rem; font-weight:900; margin:.5rem 0; }
        .hot { background:linear-gradient(135deg, rgba(241,96,99,.95), rgba(118,23,36,.7)); }
        .warm { background:linear-gradient(135deg, rgba(245,184,75,.95), rgba(120,78,12,.62)); color:#1b1305; }
        .cool { background:linear-gradient(135deg, rgba(52,211,153,.9), rgba(16,92,85,.62)); color:#041d15; }
        .mobile-form { max-width:440px; padding:18px; border-radius:22px; border:1px solid rgba(255,255,255,.12); background:#0b1625; }
        div[data-testid="stMetric"] { padding:14px; border-radius:14px; border:1px solid rgba(255,255,255,.1); background:rgba(255,255,255,.065); }
        </style>
        """,
        unsafe_allow_html=True,
    )


def chip(label: str, tone: str = "") -> str:
    return f'<span class="chip {tone}">{label}</span>'


def dashboard() -> None:
    left, right = st.columns([1.55, 0.85], gap="large")
    with left:
        st.markdown(
            """
            <div class="hero">
              <p class="subtle"><strong>CBS Safety Intelligence</strong> - A Lean Safety Operating System for Manufacturers</p>
              <h1>What needs attention today</h1>
              <p class="subtle">Plant risk is improving, but Shipping and Machine Shop need action before second shift.</p>
              <span class="chip critical">3 critical actions</span>
              <span class="chip good">91% training compliance</span>
              <span class="chip warn">JHA gap in Winding</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with right:
        st.markdown('<div class="feed"><h3>AI Safety Feed</h3>', unsafe_allow_html=True)
        for time, title, detail, tone in [
            ("8:12 AM", "AI flagged repeat pinch-point risk", "Machine Shop - press brake #4", "critical"),
            ("9:05 AM", "LOTO refresher expires for 6 employees", "Maintenance and Winding", "warn"),
            ("10:22 AM", "Corrective action verified", "Shipping dock edge guard installed", "good"),
            ("11:40 AM", "Safe act recognized", "Assembly team used stop-and-fix protocol", "good"),
        ]:
            st.markdown(f"**{time}**  \n{title}  \n<span class='subtle'>{detail}</span> {chip(tone.title(), tone)}", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    cols = st.columns(4)
    for idx, (label, value, delta, tone) in enumerate(KPI_ROWS):
        with cols[idx % 4]:
            st.markdown(f'<div class="kpi"><span>{label}</span><strong>{value}</strong><span class="{tone}">{delta}</span></div>', unsafe_allow_html=True)

    st.subheader("Department Risk Heat Map")
    heat_cols = st.columns(3)
    for idx, row in DEPARTMENTS.iterrows():
        tone = "hot" if row.Risk > 75 else "warm" if row.Risk > 55 else "cool"
        with heat_cols[idx % 3]:
            st.markdown(f'<div class="heat {tone}"><strong>{row.Department}</strong><span>Risk {row.Risk}</span><small>{row.Hazards} open hazards - Shift {row.Shift}</small></div>', unsafe_allow_html=True)

    st.subheader("Priority Action Center")
    st.dataframe(ACTIONS, use_container_width=True, hide_index=True)


def setup_page() -> None:
    st.subheader("Login / Company Setup")
    col1, col2 = st.columns(2)
    with col1:
        st.text_input("Company name", "CBS Manufacturing")
        st.text_area("Locations", "Cleveland Plant\nWest Dock\nService Center")
        st.multiselect("Departments", DEPARTMENTS.Department.tolist(), default=DEPARTMENTS.Department.tolist())
    with col2:
        st.multiselect("Shifts", ["A Shift", "B Shift", "C Shift"], default=["A Shift", "B Shift", "C Shift"])
        st.multiselect("Roles", ["Admin", "Safety Manager", "Supervisor", "Team Leader", "Employee"], default=["Admin", "Safety Manager", "Supervisor", "Team Leader", "Employee"])
        st.button("Save company setup", type="primary")


def report_page() -> None:
    st.subheader("Employee Hazard Reporting")
    st.markdown('<div class="mobile-form">', unsafe_allow_html=True)
    st.file_uploader("Take/upload photo", type=["png", "jpg", "jpeg"])
    report_type = st.segmented_control("Type", ["Hazard", "Near Miss", "Unsafe Act", "Safe Act", "Improvement Idea"], default="Hazard")
    area = st.selectbox("Area / Department", DEPARTMENTS.Department.tolist())
    comment = st.text_area("Optional comment", placeholder="What happened? Keep it simple.")
    submitted = st.button("Submit report", type="primary", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
    if submitted:
        st.success(f"{report_type} submitted for {area}. AI analysis drafted.")
        ai_analysis(comment or "Forklift crossed pedestrian aisle near dock 3.")


def ai_analysis(context: str = "") -> None:
    st.subheader("AI Hazard Analysis")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Category", "Machine Guarding")
    col2.metric("Severity", "Serious")
    col3.metric("Probability", "Likely")
    col4.metric("Risk Score", "18 / 25")
    st.markdown(
        """
        **Recommended immediate containment:** Stop use of the affected equipment or area and barricade exposure until supervisor verification.

        **Recommended corrective action:** Install engineered control, update JHA, retrain affected employees, and require before/after photo verification.

        **Similar past issues:** HZ-1880, HZ-1934, CA-0941
        """
    )


def root_cause_page() -> None:
    st.subheader("AI Root Cause Analysis")
    left, right = st.columns([0.85, 1.15], gap="large")
    with left:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### Incident details")
        st.text_area("Summary", "Maintenance technician cut left index finger while replacing slitter blade on Winding line 2.")
        st.selectbox("Injury type", ["Laceration", "Sprain", "Burn", "Contusion"])
        st.selectbox("Body part", ["Hand/finger", "Arm", "Back", "Eye"])
        st.text_area("Approved root cause", "Blade change method allowed hand exposure during alignment.")
        st.markdown("</div>", unsafe_allow_html=True)
    with right:
        tabs = st.tabs(["5 Why", "Fishbone", "5M1E", "Fault Tree", "FMEA", "Pareto", "Action Plan"])
        content = [
            "Why was hand exposed? No fixture. Why no fixture? Task evolved without JHA update.",
            "Methods, machine guarding, training, material handling, environment, and measurement factors mapped.",
            "Man: new tech. Machine: blade cart gap. Method: informal alignment. Environment: low light.",
            "Top event linked to missing fixture, expired JHA, and incomplete verification.",
            "Highest RPN: manual blade alignment. Recommended control: engineered fixture.",
            "Blade change issues represent 26% of Winding maintenance hazards.",
            "Create fixture, revise JHA, train team, verify with before/after photos.",
        ]
        for tab, text in zip(tabs, content):
            with tab:
                st.text_area("Editable AI output", text, height=180)
        st.button("Approve AI output", type="primary")


def jha_page() -> None:
    st.subheader("JHA Builder")
    task = st.text_input("Job/task name", "Press brake tooling change")
    if st.button("AI draft from task name", type="primary"):
        st.info(f"Drafting JHA for {task}")
    steps = pd.DataFrame(
        [
            {"Step": "Prepare equipment", "Hazards": "Slip/trip, pinch point", "Controls": "5S, guarded tooling", "PPE": "Safety glasses"},
            {"Step": "Isolate energy", "Hazards": "Stored energy", "Controls": "LOTO verification", "PPE": "Cut gloves"},
            {"Step": "Remove guard", "Hazards": "Sharp edge", "Controls": "Two-person lift", "PPE": "Cut gloves"},
            {"Step": "Restore and verify", "Hazards": "Unexpected startup", "Controls": "Supervisor check", "PPE": "Standard PPE"},
        ]
    )
    st.data_editor(steps, use_container_width=True, num_rows="dynamic")


def training_page() -> None:
    st.subheader("Training Management")
    st.dataframe(TRAINING, use_container_width=True, hide_index=True)
    st.bar_chart(TRAINING.set_index("Training")["Complete"])


def analytics_page() -> None:
    st.subheader("Analytics")
    col1, col2 = st.columns(2)
    with col1:
        st.bar_chart(DEPARTMENTS.set_index("Department")[["Risk", "Hazards"]])
    with col2:
        st.line_chart(DEPARTMENTS.set_index("Department")[["Score", "Training"]])
    st.dataframe(DEPARTMENTS, use_container_width=True, hide_index=True)


def simple_board(title: str, items: list[str]) -> None:
    st.subheader(title)
    cols = st.columns(3)
    for idx, item in enumerate(items):
        with cols[idx % 3]:
            st.markdown(f'<div class="card"><h3>{item}</h3><p class="subtle">Production-ready workflow placeholder with mock data.</p></div>', unsafe_allow_html=True)


inject_css()

with st.sidebar:
    st.markdown("## CBS Safety Intelligence")
    st.caption("Lean Safety OS")
    page = st.radio(
        "Module",
        [
            "Dashboard",
            "Company Setup",
            "Hazard Reporting",
            "AI Hazard Analysis",
            "Corrective Actions",
            "Incident Investigation",
            "AI Root Cause",
            "JHA Builder",
            "Safety Observations",
            "Training",
            "Lean Safety / QDIPS",
            "Recognition",
            "Analytics",
            "Admin Settings",
        ],
    )

if page == "Dashboard":
    dashboard()
elif page == "Company Setup":
    setup_page()
elif page == "Hazard Reporting":
    report_page()
elif page == "AI Hazard Analysis":
    ai_analysis()
elif page == "Corrective Actions":
    st.subheader("Corrective Action System")
    st.data_editor(ACTIONS, use_container_width=True, hide_index=True)
elif page == "Incident Investigation":
    simple_board("Incident Investigation", ["Incident details", "People involved", "Injury type", "Body part", "Location", "Photos/documents", "Witness notes", "Immediate containment", "Root cause", "Corrective action"])
elif page == "AI Root Cause":
    root_cause_page()
elif page == "JHA Builder":
    jha_page()
elif page == "Safety Observations":
    simple_board("Safety Observations", ["Safe act", "Unsafe act", "Coaching conversation", "Gemba walk finding", "Stop-and-fix action", "Improvement suggestion"])
elif page == "Training":
    training_page()
elif page == "Lean Safety / QDIPS":
    simple_board("Lean Safety / QDIPS", ["Safety KPI board", "Daily safety metric", "Pareto symptoms", "Action plan", "Department scorecards", "Blue scheduled indicator"])
elif page == "Recognition":
    simple_board("Recognition / Engagement", ["Hazard submitted +10", "Near miss submitted +15", "Corrective action completed +20", "JHA completed +25", "Suggestion implemented +30", "Monthly leaderboard"])
elif page == "Analytics":
    analytics_page()
elif page == "Admin Settings":
    simple_board("Admin Settings", ["Departments", "Users", "Roles", "Hazard categories", "Risk matrix", "Notification rules", "Training types", "Custom safety metrics"])
