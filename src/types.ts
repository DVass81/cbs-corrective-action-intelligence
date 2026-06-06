export type InvestigationStatus =
  | "New"
  | "Assigned"
  | "Containment"
  | "Investigation"
  | "Root Cause Identified"
  | "Corrective Action"
  | "Verification"
  | "Closed";

export type Investigation = {
  id: string;
  title: string;
  department: string;
  process: string;
  product: string;
  customer: string;
  supplier: string;
  detectionDate: string;
  owner: string;
  status: InvestigationStatus;
  severity: "Low" | "Medium" | "High" | "Critical";
  type: "Quality" | "Safety" | "Delivery" | "Downtime" | "Supplier" | "Engineering";
  costImpact: number;
  rcaScore: number;
  repeat: boolean;
  problem: string;
  rootCause: string;
  correctiveAction: string;
  dueDate: string;
};

export type CorrectiveAction = {
  id: string;
  rootCause: string;
  containmentAction: string;
  correctiveAction: string;
  preventiveAction: string;
  owner: string;
  dueDate: string;
  status: "Open" | "Assigned" | "In Progress" | "Completed" | "Verified" | "Closed";
  verificationMethod: string;
  effectivenessReviewDate: string;
};
