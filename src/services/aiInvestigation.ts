import type { Investigation } from "../types";

export type AiInvestigationFinding = {
  evidenceConsidered: string[];
  findings: string[];
  confidenceLevel: number;
  missingData: string[];
  recommendedNextStep: string;
};

export function createDemoAiFinding(investigation: Investigation): AiInvestigationFinding {
  return {
    evidenceConsidered: [
      investigation.problem,
      investigation.rootCause,
      investigation.correctiveAction,
      `${investigation.department} process history`,
    ],
    findings: [
      "Evidence indicates a process control weakness rather than an isolated individual mistake.",
      "The corrective action should change the operating system and include verification evidence.",
    ],
    confidenceLevel: investigation.rcaScore,
    missingData: [
      "Objective evidence sample size",
      "Prior occurrence search",
      "Control owner confirmation",
      "Effectiveness review criteria",
    ],
    recommendedNextStep: "Validate the root cause against transaction, inspection, and recurrence evidence before closure.",
  };
}
