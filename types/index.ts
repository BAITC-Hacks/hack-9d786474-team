export interface TaskDraft {
  id: string;
  rawText: string;
  industry: string;
  /** ISO 8601 timestamp. */
  createdAt: string;
}

export interface TeamProfile {
  id: string;
  name: string;
  interests: string[];
  skills: string[];
  technologies: string[];
}

export interface Proposal {
  id: string;
  taskId: string;
  teamId: string;
  solutionIdea: string;
  plan: string;
  timeline: string;
  prototypeLink: string;
  status: 'pending' | 'accepted' | 'rejected';
}
