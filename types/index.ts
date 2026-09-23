export interface TeamProfile {
  id: string;
  name: string;
  interests: string[];
  skills: string[];
  technologies: string[];
}

export type ProposalStatus = 'pending' | 'accepted' | 'rejected';

export interface Proposal {
  id: string;
  task_id: string;
  team_id: string;
  idea: string;
  plan: string;
  deadline: string;
  prototype_link: string;
  status: ProposalStatus;
  created_at: string;
}
