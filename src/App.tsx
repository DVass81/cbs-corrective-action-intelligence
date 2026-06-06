import {
  AlertTriangle,
  BarChart3,
  Bot,
  BrainCircuit,
  Building2,
  CheckCircle2,
  ClipboardCheck,
  Factory,
  FileText,
  Gauge,
  GitBranch,
  LayoutDashboard,
  Library,
  LineChart,
  Menu,
  Network,
  Plus,
  Search,
  Settings,
  ShieldCheck,
  Sparkles,
  Target,
  TimerReset,
  Wrench,
  X,
  type LucideIcon,
} from "lucide-react";
import { useMemo, useState, type ReactElement, type ReactNode } from "react";
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ComposedChart,
  Line,
  Pie,
  PieChart,
  ResponsiveContainer,
  Scatter,
  ScatterChart,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { create } from "zustand";
import { correctiveActions, departmentPerformance, investigations, monthlyTrend, paretoData } from "./data/demoData";
import { cn, currency } from "./lib/utils";
import { createDemoAiFinding } from "./services/aiInvestigation";
import type { Investigation } from "./types";

type Page =
  | "Landing"
  | "Dashboard"
  | "Investigations"
  | "New Investigation"
  | "RCA Toolbox"
  | "Corrective Actions"
  | "AI Assistant"
  | "Reports"
  | "Knowledge Center"
  | "Settings";

type AppStore = {
  selectedInvestigation: Investigation;
  setSelectedInvestigation: (investigation: Investigation) => void;
};

const useAppStore = create<AppStore>((set) => ({
  selectedInvestigation: investigations[1],
  setSelectedInvestigation: (selectedInvestigation) => set({ selectedInvestigation }),
}));

const pages: { name: Page; icon: LucideIcon }[] = [
  { name: "Landing", icon: Building2 },
  { name: "Dashboard", icon: LayoutDashboard },
  { name: "Investigations", icon: Search },
  { name: "New Investigation", icon: Plus },
  { name: "RCA Toolbox", icon: Wrench },
  { name: "Corrective Actions", icon: ClipboardCheck },
  { name: "AI Assistant", icon: Bot },
  { name: "Reports", icon: FileText },
  { name: "Knowledge Center", icon: Library },
  { name: "Settings", icon: Settings },
];

const statusColors = ["#28a8ff", "#72ddff", "#8a95a6", "#ffffff", "#3f4a5a", "#1f6feb", "#00d084", "#f4b942"];

function App() {
  const [page, setPage] = useState<Page>("Dashboard");
  const [navOpen, setNavOpen] = useState(false);

  return (
    <div className="min-h-screen bg-obsidian text-white">
      <div className="fixed inset-0 bg-[radial-gradient(circle_at_20%_10%,rgba(40,168,255,.14),transparent_28%),linear-gradient(135deg,#05070a_0%,#0c1016_46%,#111827_100%)]" />
      <div className="relative flex min-h-screen">
        <aside className={cn("sidebar", navOpen && "sidebar-open")}>
          <div className="flex items-center gap-3 border-b border-white/10 px-5 py-5">
            <div className="grid h-10 w-10 place-items-center rounded bg-electric shadow-glow">
              <Factory className="h-6 w-6 text-obsidian" />
            </div>
            <div>
              <div className="text-sm font-bold tracking-wide">CBS CAI</div>
              <div className="text-xs text-steel">Corrective Action Intelligence</div>
            </div>
          </div>
          <nav className="space-y-1 p-3">
            {pages.map((item) => {
              const Icon = item.icon;
              return (
                <button
                  key={item.name}
                  onClick={() => {
                    setPage(item.name);
                    setNavOpen(false);
                  }}
                  className={cn("nav-button", page === item.name && "nav-button-active")}
                >
                  <Icon className="h-4 w-4" />
                  <span>{item.name}</span>
                </button>
              );
            })}
          </nav>
        </aside>

        <main className="min-w-0 flex-1 lg:ml-72">
          <header className="sticky top-0 z-30 border-b border-white/10 bg-obsidian/80 px-4 py-4 backdrop-blur-xl md:px-8">
            <div className="flex items-center justify-between gap-4">
              <div className="flex items-center gap-3">
                <button className="icon-button lg:hidden" onClick={() => setNavOpen(true)} aria-label="Open navigation">
                  <Menu className="h-5 w-5" />
                </button>
                <div>
                  <p className="text-xs uppercase tracking-[.24em] text-cyanline">Custom Business Solutions</p>
                  <h1 className="text-xl font-semibold md:text-2xl">{page}</h1>
                </div>
              </div>
              <div className="hidden items-center gap-3 md:flex">
                <div className="rounded border border-white/10 bg-white/[.04] px-3 py-2 text-sm text-steel">
                  AI readiness: <span className="text-cyanline">OpenAI-ready</span>
                </div>
                <button className="primary-button">
                  <Sparkles className="h-4 w-4" />
                  Executive Report
                </button>
              </div>
            </div>
          </header>
          <div className="p-4 md:p-8">{renderPage(page)}</div>
        </main>
      </div>
      {navOpen && (
        <button className="fixed inset-0 z-30 bg-black/60 lg:hidden" onClick={() => setNavOpen(false)} aria-label="Close navigation">
          <X className="absolute right-4 top-4 h-6 w-6" />
        </button>
      )}
    </div>
  );
}

function renderPage(page: Page) {
  switch (page) {
    case "Landing":
      return <Landing />;
    case "Dashboard":
      return <Dashboard />;
    case "Investigations":
      return <Investigations />;
    case "New Investigation":
      return <NewInvestigation />;
    case "RCA Toolbox":
      return <RcaToolbox />;
    case "Corrective Actions":
      return <CorrectiveActions />;
    case "AI Assistant":
      return <AiAssistantPage />;
    case "Reports":
      return <Reports />;
    case "Knowledge Center":
      return <KnowledgeCenter />;
    case "Settings":
      return <SettingsPage />;
  }
}

function Landing() {
  return (
    <section className="min-h-[calc(100vh-120px)] overflow-hidden rounded border border-white/10 bg-carbon/70 shadow-panel">
      <div className="grid min-h-[calc(100vh-120px)] gap-8 p-6 md:grid-cols-[1.1fr_.9fr] md:p-10">
        <div className="flex max-w-3xl flex-col justify-center">
          <p className="mb-4 text-sm font-semibold uppercase tracking-[.24em] text-cyanline">CBS Corrective Action Intelligence™</p>
          <h2 className="text-4xl font-bold leading-tight md:text-6xl">Find the Cause. Fix the System. Prevent Recurrence.</h2>
          <p className="mt-6 text-lg leading-8 text-steel">
            An enterprise-grade AI decision support platform for root cause analysis, corrective action management, Lean
            improvement, and organizational learning in manufacturing environments.
          </p>
          <div className="mt-8 grid gap-3 sm:grid-cols-3">
            {["Lean Black Belt guidance", "Manufacturing RCA workflows", "Executive-ready CAPA reporting"].map((item) => (
              <div key={item} className="metric-card">
                <ShieldCheck className="mb-3 h-5 w-5 text-cyanline" />
                <span className="text-sm text-white">{item}</span>
              </div>
            ))}
          </div>
        </div>
        <div className="relative flex items-center">
          <div className="absolute inset-6 rounded-full bg-electric/10 blur-3xl" />
          <div className="relative w-full rounded border border-white/10 bg-black/30 p-5 backdrop-blur">
            <DashboardMini />
          </div>
        </div>
      </div>
    </section>
  );
}

function Dashboard() {
  const metrics = useMemo(() => {
    const open = investigations.filter((i) => i.status !== "Closed").length;
    return [
      { label: "Open Investigations", value: open, icon: AlertTriangle, delta: "+8%" },
      { label: "Closed Investigations", value: 42, icon: CheckCircle2, delta: "+14%" },
      { label: "Overdue Actions", value: 7, icon: TimerReset, delta: "-3%" },
      { label: "Repeat Issues", value: investigations.filter((i) => i.repeat).length, icon: GitBranch, delta: "+2" },
      { label: "Cost of Poor Quality", value: currency(investigations.reduce((sum, i) => sum + i.costImpact, 0)), icon: Gauge, delta: "-11%" },
      { label: "Safety Incidents", value: 3, icon: ShieldCheck, delta: "0 recordables" },
      { label: "Customer Complaints", value: 9, icon: Building2, delta: "-6%" },
      { label: "Average RCA Score", value: Math.round(investigations.reduce((sum, i) => sum + i.rcaScore, 0) / investigations.length), icon: BrainCircuit, delta: "+5 pts" },
    ];
  }, []);

  return (
    <div className="space-y-6">
      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {metrics.map((metric) => {
          const Icon = metric.icon;
          return (
            <article className="metric-card" key={metric.label}>
              <div className="flex items-center justify-between">
                <Icon className="h-5 w-5 text-cyanline" />
                <span className="text-xs text-steel">{metric.delta}</span>
              </div>
              <div className="mt-5 text-2xl font-semibold">{metric.value}</div>
              <div className="mt-1 text-sm text-steel">{metric.label}</div>
            </article>
          );
        })}
      </section>
      <section className="grid gap-6 xl:grid-cols-3">
        <Panel title="Pareto Chart" icon={BarChart3} className="xl:col-span-2">
          <Chart height={320}>
            <ComposedChart data={paretoData}>
              <CartesianGrid stroke="#263241" />
              <XAxis dataKey="cause" stroke="#8a95a6" />
              <YAxis stroke="#8a95a6" />
              <Tooltip contentStyle={tooltipStyle} />
              <Bar dataKey="count" fill="#28a8ff" radius={[4, 4, 0, 0]} />
              <Line dataKey="cumulative" stroke="#72ddff" strokeWidth={3} />
            </ComposedChart>
          </Chart>
        </Panel>
        <Panel title="Status Distribution" icon={Target}>
          <Chart height={320}>
            <PieChart>
              <Pie data={statusDistribution()} dataKey="value" nameKey="name" outerRadius={110} innerRadius={62}>
                {statusDistribution().map((_, index) => (
                  <Cell key={index} fill={statusColors[index % statusColors.length]} />
                ))}
              </Pie>
              <Tooltip contentStyle={tooltipStyle} />
            </PieChart>
          </Chart>
        </Panel>
      </section>
      <section className="grid gap-6 xl:grid-cols-2">
        <Panel title="Monthly Trends" icon={LineChart}>
          <Chart height={280}>
            <AreaChart data={monthlyTrend}>
              <CartesianGrid stroke="#263241" />
              <XAxis dataKey="month" stroke="#8a95a6" />
              <YAxis stroke="#8a95a6" />
              <Tooltip contentStyle={tooltipStyle} />
              <Area type="monotone" dataKey="open" stroke="#28a8ff" fill="#28a8ff33" />
              <Area type="monotone" dataKey="closed" stroke="#72ddff" fill="#72ddff22" />
            </AreaChart>
          </Chart>
        </Panel>
        <Panel title="Department Performance" icon={Factory}>
          <Chart height={280}>
            <BarChart data={departmentPerformance} layout="vertical">
              <CartesianGrid stroke="#263241" />
              <XAxis type="number" stroke="#8a95a6" />
              <YAxis type="category" dataKey="department" stroke="#8a95a6" width={90} />
              <Tooltip contentStyle={tooltipStyle} />
              <Bar dataKey="score" fill="#72ddff" radius={[0, 4, 4, 0]} />
            </BarChart>
          </Chart>
        </Panel>
      </section>
      <Pipeline />
    </div>
  );
}

function Investigations() {
  const { selectedInvestigation, setSelectedInvestigation } = useAppStore();
  return (
    <div className="grid gap-6 xl:grid-cols-[1.4fr_.9fr]">
      <Panel title="Investigation Portfolio" icon={Search}>
        <div className="overflow-x-auto">
          <table className="data-table">
            <thead>
              <tr>
                <th>Number</th>
                <th>Title</th>
                <th>Status</th>
                <th>Owner</th>
                <th>Cost</th>
                <th>Score</th>
              </tr>
            </thead>
            <tbody>
              {investigations.map((item) => (
                <tr key={item.id} onClick={() => setSelectedInvestigation(item)} className={cn(selectedInvestigation.id === item.id && "selected-row")}>
                  <td>{item.id}</td>
                  <td>{item.title}</td>
                  <td><StatusPill value={item.status} /></td>
                  <td>{item.owner}</td>
                  <td>{currency(item.costImpact)}</td>
                  <td>{item.rcaScore}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Panel>
      <AiPanel investigation={selectedInvestigation} />
    </div>
  );
}

function NewInvestigation() {
  return (
    <div className="grid gap-6 xl:grid-cols-[1.2fr_.8fr]">
      <Panel title="New Investigation Wizard" icon={Plus}>
        <div className="grid gap-4 md:grid-cols-2">
          {["Investigation Number", "Title", "Department", "Process", "Product", "Customer", "Supplier", "Detection Date", "Investigation Owner"].map((field) => (
            <label className="field" key={field}>
              <span>{field}</span>
              <input placeholder={field} />
            </label>
          ))}
          {["Quality Impact", "Safety Impact", "Delivery Impact", "Financial Impact"].map((field) => (
            <label className="field" key={field}>
              <span>{field}</span>
              <select>
                <option>Low</option>
                <option>Medium</option>
                <option>High</option>
                <option>Critical</option>
              </select>
            </label>
          ))}
          {["Problem Description", "What Happened", "Where", "When", "Who Found It", "Initial Containment Actions"].map((field) => (
            <label className="field md:col-span-2" key={field}>
              <span>{field}</span>
              <textarea placeholder={field} rows={field === "Problem Description" ? 4 : 2} />
            </label>
          ))}
        </div>
      </Panel>
      <Panel title="AI Problem Statement Rewrite" icon={Sparkles}>
        <div className="rounded border border-cyanline/30 bg-electric/10 p-4 text-sm leading-7">
          Objective statement: On 2026-05-08, purchasing released a purchase order for C110 copper instead of required C101
          copper for bus bar assembly, resulting in production hold, replacement expedite cost, and customer delivery risk.
        </div>
        <AnalysisList />
      </Panel>
    </div>
  );
}

function RcaToolbox() {
  const tools: { name: string; icon: LucideIcon }[] = [
    { name: "Five Why Analysis", icon: Network },
    { name: "Fishbone Diagram", icon: GitBranch },
    { name: "5M + 1E Matrix", icon: Factory },
    { name: "Fault Tree Analysis", icon: BrainCircuit },
    { name: "FMEA Module", icon: Gauge },
    { name: "Pareto Analysis", icon: BarChart3 },
    { name: "Scatter Analysis", icon: LineChart },
    { name: "Process Mapping", icon: Target },
  ];
  const scatterData = [
    { x: 12, y: 2.1, z: 80 },
    { x: 18, y: 3.4, z: 120 },
    { x: 24, y: 4.2, z: 160 },
    { x: 31, y: 7.8, z: 210 },
    { x: 37, y: 8.4, z: 250 },
    { x: 42, y: 9.1, z: 270 },
  ];
  return (
    <div className="space-y-6">
      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {tools.map(({ name, icon: Icon }) => (
          <article className="tool-card" key={name}>
            <Icon className="h-6 w-6 text-cyanline" />
            <h3>{name}</h3>
            <p>AI-assisted investigation workflow with evidence prompts, weak-answer detection, and action generation.</p>
          </article>
        ))}
      </section>
      <div className="grid gap-6 xl:grid-cols-2">
        <FiveWhy />
        <Fishbone />
        <Fmea />
        <FaultTree />
        <Panel title="Scatter Analysis" icon={LineChart}>
          <Chart height={280}>
            <ScatterChart>
              <CartesianGrid stroke="#263241" />
              <XAxis dataKey="x" name="Fixture Age" stroke="#8a95a6" />
              <YAxis dataKey="y" name="Scrap Rate" stroke="#8a95a6" />
              <Tooltip contentStyle={tooltipStyle} cursor={{ strokeDasharray: "3 3" }} />
              <Scatter name="Scrap correlation" data={scatterData} fill="#72ddff" />
            </ScatterChart>
          </Chart>
        </Panel>
        <Panel title="Process Mapping" icon={Target}>
          <div className="pipeline">
            {["Supplier", "Incoming", "Production", "Inspection", "Pack", "Ship"].map((step) => (
              <div key={step}>
                <span>{step}</span>
                <strong>{step === "Inspection" ? "Risk" : "OK"}</strong>
              </div>
            ))}
          </div>
        </Panel>
      </div>
    </div>
  );
}

function CorrectiveActions() {
  return (
    <Panel title="CAPA Management" icon={ClipboardCheck}>
      <div className="overflow-x-auto">
        <table className="data-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Root Cause</th>
              <th>Corrective Action</th>
              <th>Owner</th>
              <th>Due</th>
              <th>Status</th>
              <th>Verification</th>
            </tr>
          </thead>
          <tbody>
            {correctiveActions.map((action) => (
              <tr key={action.id}>
                <td>{action.id}</td>
                <td>{action.rootCause}</td>
                <td>{action.correctiveAction}</td>
                <td>{action.owner}</td>
                <td>{action.dueDate}</td>
                <td><StatusPill value={action.status} /></td>
                <td>{action.verificationMethod}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Panel>
  );
}

function AiAssistantPage() {
  const { selectedInvestigation } = useAppStore();
  return (
    <div className="grid gap-6 xl:grid-cols-[.9fr_1.1fr]">
      <AiPanel investigation={selectedInvestigation} />
      <Panel title="Lean Intelligence Engine" icon={BrainCircuit}>
        <div className="grid gap-4 md:grid-cols-2">
          {[
            ["Poka-Yoke", "Prevents wrong revision or wrong material selection at the transaction point.", "Medium", "High"],
            ["Layered Process Audits", "Confirms the control remains active after launch.", "Low", "Medium"],
            ["Control Plan Update", "Converts investigation learning into a governed process control.", "Medium", "High"],
            ["Standard Work", "Makes the verified sequence visible and repeatable across shifts.", "Low", "High"],
            ["TPM", "Adds early detection before machine failure affects output.", "Medium", "Medium"],
            ["A3 Problem Solving", "Structures learning and executive review in one document.", "Low", "Medium"],
          ].map(([name, why, difficulty, impact]) => (
            <div className="recommendation" key={name}>
              <h3>{name}</h3>
              <p>{why}</p>
              <div className="mt-4 flex gap-2 text-xs">
                <span>Difficulty: {difficulty}</span>
                <span>Impact: {impact}</span>
              </div>
            </div>
          ))}
        </div>
      </Panel>
    </div>
  );
}

function Reports() {
  const { selectedInvestigation } = useAppStore();
  return (
    <Panel title="AI Report Generator" icon={FileText}>
      <div className="report">
        <div>
          <p className="text-xs uppercase tracking-[.22em] text-cyanline">Executive RCA Report</p>
          <h2>{selectedInvestigation.title}</h2>
          <p className="text-steel">{selectedInvestigation.id} | Owner: {selectedInvestigation.owner} | Cost impact: {currency(selectedInvestigation.costImpact)}</p>
        </div>
        {["Executive Summary", "Problem Statement", "Timeline", "Evidence", "Investigation Tools Used", "Root Cause", "Contributing Causes", "Corrective Actions", "Preventive Actions", "Verification Plan", "Lessons Learned", "Approval Signatures"].map((section) => (
          <section key={section}>
            <h3>{section}</h3>
            <p>
              {section === "Root Cause" ? selectedInvestigation.rootCause : section === "Corrective Actions" ? selectedInvestigation.correctiveAction : "Generated report content is structured for executive review, plant leadership approval, and audit-ready CAPA records."}
            </p>
          </section>
        ))}
      </div>
      <div className="mt-5 flex flex-wrap gap-3">
        <button className="primary-button">Export PDF</button>
        <button className="secondary-button">Export Word</button>
        <button className="secondary-button">Print View</button>
      </div>
    </Panel>
  );
}

function KnowledgeCenter() {
  return (
    <div className="grid gap-6 xl:grid-cols-3">
      {["Lessons Learned", "Best Practices", "Proven Corrective Actions", "Investigation Templates", "Repeat Failure Signals", "Supplier Trends"].map((title) => (
        <Panel title={title} icon={Library} key={title}>
          <p className="text-sm leading-7 text-steel">
            Indexed organizational learning from prior investigations, successful controls, failed action patterns, and
            recurring root causes. Future OpenAI integration can retrieve these records for context-aware recommendations.
          </p>
        </Panel>
      ))}
    </div>
  );
}

function SettingsPage() {
  return (
    <Panel title="Enterprise Settings" icon={Settings}>
      <div className="grid gap-4 md:grid-cols-2">
        {["OpenAI API Integration", "Approval Workflow", "Role-Based Access", "Departments", "Supplier Master", "Report Templates", "Audit Trail", "Data Retention"].map((setting) => (
          <div className="setting-row" key={setting}>
            <div>
              <h3>{setting}</h3>
              <p>Configured for production enterprise deployment.</p>
            </div>
            <button className="secondary-button">Configure</button>
          </div>
        ))}
      </div>
    </Panel>
  );
}

function AiPanel({ investigation }: { investigation: Investigation }) {
  const finding = createDemoAiFinding(investigation);
  return (
    <Panel title="AI Investigation Assistant" icon={Bot}>
      <div className="space-y-4">
        <div className="rounded border border-white/10 bg-white/[.04] p-4">
          <p className="text-sm text-steel">Active investigation</p>
          <h3 className="mt-1 text-lg font-semibold">{investigation.title}</h3>
          <p className="mt-3 text-sm leading-7 text-steel">{investigation.problem}</p>
        </div>
        <AnalysisList finding={finding} />
        <div className="rounded border border-cyanline/30 bg-electric/10 p-4">
          <div className="mb-2 flex items-center justify-between">
            <span className="text-sm font-semibold text-cyanline">Confidence Level</span>
            <span className="text-sm">{finding.confidenceLevel}%</span>
          </div>
          <div className="h-2 rounded bg-white/10">
            <div className="h-2 rounded bg-cyanline" style={{ width: `${finding.confidenceLevel}%` }} />
          </div>
        </div>
      </div>
    </Panel>
  );
}

function AnalysisList({ finding }: { finding?: ReturnType<typeof createDemoAiFinding> }) {
  const rows = [
    ["Evidence Considered", finding?.evidenceConsidered.join("; ") ?? "Nonconformance record, ERP transaction history, inspection records, customer impact, prior CAPA history."],
    ["Findings", finding?.findings.join(" ") ?? "Current evidence points to a system control gap rather than isolated operator error."],
    ["Missing Data", finding?.missingData.join("; ") ?? "Need approval history, training record, first occurrence date, and post-action verification sample size."],
    ["Recommended Next Step", finding?.recommendedNextStep ?? "Complete 5-Why branch on approval control failure and validate with objective transaction evidence."],
  ];
  return (
    <div className="space-y-3">
      {rows.map(([label, value]) => (
        <div className="analysis-row" key={label}>
          <span>{label}</span>
          <p>{value}</p>
        </div>
      ))}
    </div>
  );
}

function FiveWhy() {
  const whys = [
    "Why was the wrong material ordered?",
    "Why did ERP allow substitute material?",
    "Why was engineering approval not required?",
    "Why was the control plan not linked to purchasing fields?",
    "Why are item master changes not risk-reviewed?",
  ];
  return (
    <Panel title="Five Why Analysis" icon={Network}>
      <div className="space-y-3">
        {whys.map((why, index) => (
          <div className="why-row" key={why}>
            <span>{index + 1}</span>
            <div>
              <h4>{why}</h4>
              <p>{index < 4 ? "AI prompt: strengthen answer with evidence and avoid stopping at a symptom." : "Root cause candidate: governance gap in item master risk review."}</p>
            </div>
          </div>
        ))}
      </div>
    </Panel>
  );
}

function Fishbone() {
  const categories = ["People", "Machine", "Method", "Material", "Measurement", "Environment"];
  return (
    <Panel title="Fishbone Diagram" icon={GitBranch}>
      <div className="fishbone">
        {categories.map((category) => (
          <div key={category}>
            <h4>{category}</h4>
            <p>AI suggested cause</p>
          </div>
        ))}
      </div>
    </Panel>
  );
}

function Fmea() {
  const rows = [
    ["Wrong revision used", 9, 4, 5],
    ["Surface finish drift", 8, 5, 4],
    ["Supplier late delivery", 6, 7, 6],
  ];
  return (
    <Panel title="FMEA Module" icon={Gauge}>
      <div className="overflow-x-auto">
        <table className="data-table compact">
          <thead><tr><th>Failure Mode</th><th>S</th><th>O</th><th>D</th><th>RPN</th></tr></thead>
          <tbody>
            {rows.map(([mode, s, o, d]) => (
              <tr key={String(mode)}><td>{mode}</td><td>{s}</td><td>{o}</td><td>{d}</td><td>{Number(s) * Number(o) * Number(d)}</td></tr>
            ))}
          </tbody>
        </table>
      </div>
    </Panel>
  );
}

function FaultTree() {
  return (
    <Panel title="Fault Tree Analysis" icon={BrainCircuit}>
      <div className="fault-tree">
        <div>Top Event: Repeat customer defect</div>
        <div className="gate">OR</div>
        <div className="grid gap-3 sm:grid-cols-3">
          <span>Control escaped</span>
          <span>Process drifted</span>
          <span>Spec unclear</span>
        </div>
      </div>
    </Panel>
  );
}

function Pipeline() {
  const statuses = ["New", "Assigned", "Containment", "Investigation", "Root Cause Identified", "Corrective Action", "Verification", "Closed"];
  return (
    <Panel title="Investigation Pipeline" icon={GitBranch}>
      <div className="pipeline">
        {statuses.map((status) => (
          <div key={status}>
            <span>{status}</span>
            <strong>{investigations.filter((i) => i.status === status).length}</strong>
          </div>
        ))}
      </div>
    </Panel>
  );
}

function DashboardMini() {
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-3 gap-3">
        <div className="mini-stat">Open<br /><strong>21</strong></div>
        <div className="mini-stat">RCA Score<br /><strong>82</strong></div>
        <div className="mini-stat">COPQ<br /><strong>$499K</strong></div>
      </div>
      <Chart height={220}>
        <AreaChart data={monthlyTrend}>
          <Area type="monotone" dataKey="cost" stroke="#28a8ff" fill="#28a8ff33" />
        </AreaChart>
      </Chart>
      <div className="grid grid-cols-4 gap-2">
        {["New", "Containment", "RCA", "Verified"].map((item) => <span className="mini-pill" key={item}>{item}</span>)}
      </div>
    </div>
  );
}

function StatusPill({ value }: { value: string }) {
  return <span className="status-pill">{value}</span>;
}

function Panel({ title, icon: Icon, className, children }: { title: string; icon: LucideIcon; className?: string; children: ReactNode }) {
  return (
    <section className={cn("panel", className)}>
      <div className="mb-5 flex items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <Icon className="h-5 w-5 text-cyanline" />
          <h2 className="text-lg font-semibold">{title}</h2>
        </div>
      </div>
      {children}
    </section>
  );
}

function Chart({ height, children }: { height: number; children: ReactElement }) {
  return <ResponsiveContainer width="100%" height={height}>{children}</ResponsiveContainer>;
}

function statusDistribution() {
  return ["New", "Assigned", "Containment", "Investigation", "Root Cause Identified", "Corrective Action", "Verification", "Closed"].map((status) => ({
    name: status,
    value: investigations.filter((i) => i.status === status).length,
  }));
}

const tooltipStyle = {
  background: "#0c1016",
  border: "1px solid rgba(255,255,255,.14)",
  borderRadius: 4,
  color: "#fff",
};

export default App;
