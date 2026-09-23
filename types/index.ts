export interface TaskDraft {
  id: string;
  rawText: string;
  industry: string;
  /** ISO 8601 timestamp. */
  createdAt: string;
}

export interface TaskCard {
  id: string;
  title: string;
  contextAndNeed: string;
  dataAndMaterials: string;
  expectedResult: string;
  successCriteria: string;
  constraints: string;
  users: string;
  businessContact: string;
  /** Completeness score from 0 to 100. */
  score: number;
  status: 'draft' | 'workable' | 'ready' | 'priority';
  isConfirmed: boolean;
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
