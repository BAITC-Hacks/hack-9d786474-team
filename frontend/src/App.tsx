import { useEffect, useState } from 'react';
import { RatingWidget } from './components/RatingWidget';
import { TaskBuilder, type Task } from './components/TaskBuilder';
import { TaskCatalog } from './components/TaskCatalog';

type Team = { id: string; name: string; description: string; members: string[]; contacts: Record<string, string> };
type Proposal = { id: string; task_id: string; team_id: string; idea: string; plan: string; deadline: string; prototype_link: string; status: 'submitted' | 'accepted' | 'rejected'; created_at: string; updated_at: string };
type Screen = 'create' | 'catalog' | 'dashboard';

async function api<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(path, { headers: { 'Content-Type': 'application/json' }, ...init });
  if (!response.ok) throw new Error((await response.text()) || `API error ${response.status}`);
  return response.status === 204 ? (undefined as T) : response.json();
}

export default function App() {
  const [screen, setScreen] = useState<Screen>('create');
  const [tasks, setTasks] = useState<Task[]>([]);
  const [teams, setTeams] = useState<Team[]>([]);
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);
  const [proposals, setProposals] = useState<Proposal[]>([]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  async function refreshCatalog() {
    setLoading(true); setError('');
    try { setTasks(await api<Task[]>('/catalog')); } catch (cause) { setError(cause instanceof Error ? cause.message : 'Не удалось загрузить каталог'); } finally { setLoading(false); }
  }

  useEffect(() => { void refreshCatalog(); api<Team[]>('/teams').then(setTeams).catch(() => undefined); }, []);

  async function openTask(task: Task) {
    setSelectedTask(task); setScreen('dashboard'); setError('');
    try { setProposals(await api<Proposal[]>(`/tasks/${task.id}/proposals`)); } catch (cause) { setError(cause instanceof Error ? cause.message : 'Не удалось загрузить предложения'); }
  }

  async function updateProposal(id: string, status: Proposal['status']) {
    try {
      const updated = await api<Proposal>(`/proposals/${id}`, { method: 'PATCH', body: JSON.stringify({ status }) });
      setProposals((current) => current.map((proposal) => proposal.id === id ? updated : proposal));
    } catch (cause) { setError(cause instanceof Error ? cause.message : 'Не удалось обновить предложение'); }
  }

  return <div className="app"><div className="shell">
    <header><p className="badge">BAITC Task Platform MVP</p><h1>От задачи до предложения команды</h1><p className="muted">Единый backend-контракт Task, детерминированный rating и ручной выбор предложения.</p></header>
    <nav>
      <button className={screen === 'create' ? '' : 'secondary'} onClick={() => setScreen('create')}>Создать задачу</button>
      <button className={screen === 'catalog' ? '' : 'secondary'} onClick={() => { setScreen('catalog'); void refreshCatalog(); }}>Каталог ({tasks.length})</button>
      <button className={screen === 'dashboard' ? '' : 'secondary'} onClick={() => setScreen('dashboard')}>Dashboard</button>
    </nav>
    {error && <p className="error">{error}</p>}
    {screen === 'create' && <TaskBuilder onConfirm={async (task) => { setSelectedTask(task); await refreshCatalog(); setScreen('catalog'); }} />}
    {screen === 'catalog' && <>{loading ? <p className="panel">Загрузка каталога…</p> : <TaskCatalog tasks={tasks} onViewAndRespond={(task) => void openTask(task)} />}<p className="muted">В каталог попадают только подтверждённые задачи со статусом ready или priority.</p></>}
    {screen === 'dashboard' && <Dashboard task={selectedTask} teams={teams} proposals={proposals} onBack={() => setScreen('catalog')} onStatus={updateProposal} />}
  </div></div>;
}

function Dashboard({ task, teams, proposals, onBack, onStatus }: { task: Task | null; teams: Team[]; proposals: Proposal[]; onBack: () => void; onStatus: (id: string, status: Proposal['status']) => Promise<void> }) {
  const [teamId, setTeamId] = useState(teams[0]?.id ?? '');
  const [idea, setIdea] = useState(''); const [plan, setPlan] = useState(''); const [deadline, setDeadline] = useState(''); const [prototypeLink, setPrototypeLink] = useState(''); const [sent, setSent] = useState('');
  if (!task) return <div className="panel"><h2>Выберите задачу</h2><button className="button" onClick={onBack}>Открыть каталог</button></div>;
  const currentTask = task;
  async function submit() {
    setSent('');
    try { await api<Proposal>('/proposals', { method: 'POST', body: JSON.stringify({ task_id: currentTask.id, team_id: teamId, idea, plan, deadline, prototype_link: prototypeLink }) }); setSent('Предложение отправлено'); setIdea(''); setPlan(''); setDeadline(''); setPrototypeLink(''); } catch (cause) { setSent(cause instanceof Error ? cause.message : 'Ошибка отправки'); }
  }
  return <div><button className="button" onClick={onBack}>← Каталог</button><div className="panel"><h2>{task.title}</h2><p>{task.context_and_need}</p><p><b>Ожидаемый результат:</b> {task.expected_result}</p><RatingWidget rating_total={task.rating_total} status={task.status} rating_breakdown={task.rating_breakdown} missing_fields={task.missing_fields} /></div><div className="panel"><h2>Предложить решение</h2><label>Команда<select value={teamId} onChange={(event) => setTeamId(event.target.value)}>{teams.map((team) => <option key={team.id} value={team.id}>{team.name}</option>)}</select></label><label>Идея<textarea value={idea} onChange={(event) => setIdea(event.target.value)} /></label><label>План<textarea value={plan} onChange={(event) => setPlan(event.target.value)} /></label><label>Deadline<input value={deadline} onChange={(event) => setDeadline(event.target.value)} /></label><label>Prototype link<input value={prototypeLink} onChange={(event) => setPrototypeLink(event.target.value)} /></label><button className="button" disabled={!teamId || !idea || !plan || !deadline} onClick={() => void submit()}>Отправить предложение</button>{sent && <p className="muted">{sent}</p>}</div><div className="panel"><h2>Предложения команд</h2>{proposals.length === 0 ? <p className="muted">Предложений пока нет.</p> : proposals.map((proposal) => <ProposalCard key={proposal.id} proposal={proposal} teams={teams} onStatus={onStatus} />)}</div></div>;
}

function ProposalCard({ proposal, teams, onStatus }: { proposal: Proposal; teams: Team[]; onStatus: (id: string, status: Proposal['status']) => Promise<void> }) {
  const team = teams.find((item) => item.id === proposal.team_id);
  return <article className="card"><p className="badge">{team?.name ?? proposal.team_id} · {proposal.status}</p><h3>{proposal.idea}</h3><p>{proposal.plan}</p><p><b>Deadline:</b> {proposal.deadline}</p>{proposal.prototype_link && <p><a href={proposal.prototype_link}>{proposal.prototype_link}</a></p>}<div className="actions"><button className="button success" onClick={() => void onStatus(proposal.id, 'accepted')}>Accept</button><button className="button danger" onClick={() => void onStatus(proposal.id, 'rejected')}>Reject</button></div></article>;
}
