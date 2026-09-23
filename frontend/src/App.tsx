import { useEffect, useLayoutEffect, useMemo, useState } from 'react';
import { RatingWidget } from './components/RatingWidget';
import { TaskBuilder, type Task } from './components/TaskBuilder';
import { TaskCatalog } from './components/TaskCatalog';

type Role = 'business' | 'freelancer';
type Profile = { id: string; role: Role; name: string; company: string; headline: string; description: string; industry: string; skills: string[]; experience: string; city: string; contacts: Record<string, string>; avatar: string };
type ProfileChanges = Pick<Profile, 'name' | 'company' | 'headline' | 'description' | 'industry' | 'skills' | 'experience' | 'city' | 'contacts' | 'avatar'>;
type Team = { id: string; name: string; description: string; members: string[]; contacts: Record<string, string> };
type Proposal = { id: string; task_id: string; team_id: string; idea: string; plan: string; deadline: string; prototype_link: string; status: 'submitted' | 'accepted' | 'rejected'; created_at: string; updated_at: string };
type Screen = 'home' | 'create' | 'tasks' | 'catalog' | 'proposals' | 'projects' | 'profile';

async function api<T>(path: string, init?: RequestInit): Promise<T> { const response = await fetch(path, { headers: { 'Content-Type': 'application/json' }, ...init }); if (!response.ok) throw new Error((await response.text()) || `API error ${response.status}`); return response.json(); }
const profileIds: Record<Role, string> = { business: 'demo-business-1', freelancer: 'demo-freelancer-1' };

export default function App() {
  const [role, setRole] = useState<Role>(() => (localStorage.getItem('demo-role') as Role) || 'business');
  const [theme, setTheme] = useState<'light' | 'dark'>(() => localStorage.getItem('demo-theme') === 'dark' ? 'dark' : 'light');
  useLayoutEffect(() => {
    document.documentElement.dataset.theme = theme;
    localStorage.setItem('demo-theme', theme);
  }, [theme]);
  const [screen, setScreen] = useState<Screen>('home'); const [profile, setProfile] = useState<Profile | null>(null); const [tasks, setTasks] = useState<Task[]>([]); const [teams, setTeams] = useState<Team[]>([]); const [proposals, setProposals] = useState<Proposal[]>([]); const [selectedTask, setSelectedTask] = useState<Task | null>(null); const [error, setError] = useState(''); const [loading, setLoading] = useState(false);
  async function loadData(nextRole = role) { setLoading(true); setError(''); try { const catalog = await api<Task[]>('/catalog'); setTasks(catalog); setTeams(await api<Team[]>('/teams')); setProfile(await api<Profile>(`/profiles/${profileIds[nextRole]}`)); if (nextRole === 'freelancer') { const all = await Promise.all(catalog.map((task) => api<Proposal[]>(`/tasks/${task.id}/proposals`))); setProposals(all.flat().slice(0, 30)); } } catch (cause) { setError(cause instanceof Error ? cause.message : 'Не удалось загрузить данные'); } finally { setLoading(false); } }
  useEffect(() => { void loadData(); }, [role]);
  function switchRole(next: Role) { localStorage.setItem('demo-role', next); setRole(next); setScreen('home'); }
  async function openTask(task: Task) { setSelectedTask(task); setScreen('proposals'); try { setProposals(await api<Proposal[]>(`/tasks/${task.id}/proposals`)); } catch (cause) { setError(cause instanceof Error ? cause.message : 'Не удалось загрузить предложения'); } }
  async function updateProposal(id: string, status: Proposal['status']) { const updated = await api<Proposal>(`/proposals/${id}`, { method: 'PATCH', body: JSON.stringify({ status }) }); setProposals((items) => items.map((item) => item.id === id ? updated : item)); }
  async function saveProfile(changes: ProfileChanges) {
    if (!profile) throw new Error('Профиль не загружен');
    const updated = await api<Profile>(`/profiles/${profile.id}`, { method: 'PATCH', body: JSON.stringify(changes) });
    setProfile(updated);
    return updated;
  }
  const nav = role === 'business' ? [['home', 'Главная'], ['create', 'Создать задачу'], ['tasks', 'Мои задачи'], ['catalog', 'Каталог'], ['proposals', 'Отклики'], ['profile', 'Профиль']] : [['home', 'Главная'], ['catalog', 'Каталог задач'], ['proposals', 'Мои отклики'], ['projects', 'Мои проекты'], ['profile', 'Профиль']];
  const accepted = proposals.filter((item) => item.status === 'accepted').length;
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand"><span className="brand-mark">B</span><span>BAITC<span className="brand-muted"> / platform</span></span></div>
        <div className="profile-mini">
          <div className="avatar">{profile?.name?.slice(0, 1) || '?'}</div>
          <div><b>{profile?.company || profile?.name || 'Загрузка'}</b><small>{role === 'business' ? 'Бизнес' : 'Фрилансер / команда'}</small></div>
        </div>
        <nav className="side-nav">
          {nav.map(([id, label]) => <button key={id} className={screen === id ? 'active' : ''} onClick={() => setScreen(id as Screen)}>{label}</button>)}
        </nav>
        <div className="role-switch">
          <small>Текущий профиль</small>
          <button className={role === 'business' ? 'selected' : ''} onClick={() => switchRole('business')}>◈ Бизнес</button>
          <button className={role === 'freelancer' ? 'selected' : ''} onClick={() => switchRole('freelancer')}>◇ Фрилансер</button>
        </div>
      </aside>
      <main className="main-area">
        <header className="topbar">
          <div><span className="eyebrow">{role === 'business' ? 'Рабочее пространство бизнеса' : 'Пространство исполнителя'}</span><h1>{screen === 'home' ? 'Добро пожаловать' : nav.find(([id]) => id === screen)?.[1]}</h1></div>
          <div className="topbar-actions">
            <button className="ghost-button theme-toggle" type="button" aria-label={theme === 'light' ? 'Включить тёмную тему' : 'Включить светлую тему'} onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}>{theme === 'light' ? '☾ Тёмная тема' : '☀ Светлая тема'}</button>
            <button className="ghost-button" onClick={() => setScreen('profile')}><span className="avatar small">{profile?.name?.slice(0, 1) || '?'}</span>{profile?.name || 'Профиль'}⌄</button>
          </div>
        </header>
        {error && <div className="alert" role="alert">{error}</div>}
        {loading && <div className="loading-bar" />}
        {role === 'business' && <div className={screen === 'create' ? 'screen-transition' : 'screen-hidden'}><TaskBuilder onConfirm={async () => { await loadData(); setScreen('catalog'); }} /></div>}
        {screen !== 'create' && (
          <div key={role + '-' + screen} className="screen-transition">
            {screen === 'home' && <Home role={role} profile={profile} tasks={tasks} proposals={proposals} accepted={accepted} onCreate={() => setScreen('create')} onCatalog={() => setScreen('catalog')} onProfile={() => setScreen('profile')} />}
            {(screen === 'catalog' || screen === 'tasks') && <CatalogView tasks={screen === 'tasks' ? tasks.filter((task) => task.confirmed) : tasks} role={role} onOpen={(task) => void openTask(task)} />}
            {screen === 'proposals' && <ProposalView role={role} task={selectedTask} teams={teams} proposals={proposals} onBack={() => setScreen('catalog')} onStatus={updateProposal} onCreated={(proposal) => setProposals((items) => [proposal, ...items])} />}
            {screen === 'projects' && <ProjectsView proposals={proposals.filter((item) => item.status === 'accepted')} tasks={tasks} />}
            {screen === 'profile' && profile && <ProfileView profile={profile} role={role} proposals={proposals} onSave={saveProfile} />}
          </div>
        )}
      </main>
    </div>
  );
}

function Home({ role, profile, tasks, proposals, accepted, onCreate, onCatalog, onProfile }: { role: Role; profile: Profile | null; tasks: Task[]; proposals: Proposal[]; accepted: number; onCreate: () => void; onCatalog: () => void; onProfile: () => void }) { const stat = role === 'business' ? [{ n: tasks.length, l: 'Опубликованные задачи' }, { n: proposals.length, l: 'Отклики команд' }, { n: tasks.filter((t) => t.status === 'priority').length, l: 'Приоритетные' }] : [{ n: tasks.length, l: 'Найдено задач' }, { n: proposals.length, l: 'Мои отклики' }, { n: accepted, l: 'Принятые проекты' }]; return <><section className="hero-card"><div><span className="pill">{role === 'business' ? 'BUSINESS WORKSPACE' : 'FREELANCER WORKSPACE'}</span><h2>{role === 'business' ? 'Превращайте идеи в задачи для сильных команд.' : 'Находите задачи, где ваш опыт приносит результат.'}</h2><p>{profile?.description || 'Demo profile — данные можно изменить в профиле.'}</p><div className="actions"><button className="primary-button" onClick={role === 'business' ? onCreate : onCatalog}>{role === 'business' ? 'Создать новую задачу →' : 'Смотреть каталог →'}</button><button className="secondary-button" onClick={onProfile}>Открыть профиль</button></div></div><div className="hero-orb">{role === 'business' ? '✦' : '⌁'}</div></section><div className="stat-grid">{stat.map((item) => <div className="stat-card" key={item.l}><strong>{item.n}</strong><span>{item.l}</span></div>)}</div><section className="section-heading"><div><span className="eyebrow">Быстрый доступ</span><h2>Что хотите сделать?</h2></div></section><div className="action-grid"><button onClick={role === 'business' ? onCreate : onCatalog}><span>＋</span><b>{role === 'business' ? 'Сформировать задачу' : 'Найти новую задачу'}</b><small>{role === 'business' ? 'AI поможет уточнить требования' : 'Изучить опубликованные задачи'}</small></button><button onClick={onProfile}><span>◎</span><b>Обновить профиль</b><small>Покажите сильные стороны</small></button></div></>; }

function CatalogView({ tasks, role, onOpen }: { tasks: Task[]; role: Role; onOpen: (task: Task) => void }) { const [query, setQuery] = useState(''); const [sort, setSort] = useState('rating'); const visible = useMemo(() => tasks.filter((task) => `${task.title} ${task.context_and_need}`.toLowerCase().includes(query.toLowerCase())).slice().sort((a, b) => sort === 'rating' ? b.rating_total - a.rating_total : a.title.localeCompare(b.title)), [tasks, query, sort]); return <><div className="toolbar"><input placeholder="Поиск по задачам…" value={query} onChange={(event) => setQuery(event.target.value)} /><select value={sort} onChange={(event) => setSort(event.target.value)}><option value="rating">Сначала высокий rating</option><option value="title">По названию</option></select></div><div className="task-grid">{visible.map((task) => <article className="task-card" key={task.id}><div className="task-card-top"><span className="pill">{task.status}</span><strong>{task.rating_total}/100</strong></div><h3>{task.title}</h3><p>{task.context_and_need}</p><div className="task-result"><small>Ожидаемый результат</small><span>{task.expected_result}</span></div><button className="text-button" onClick={() => onOpen(task)}>{role === 'business' ? 'Посмотреть отклики →' : 'Посмотреть задачу →'}</button></article>)}</div>{visible.length === 0 && <div className="empty-state">Задач по этому запросу пока нет.</div>}</>; }

function ProposalView({ role, task, teams, proposals, onBack, onStatus, onCreated }: { role: Role; task: Task | null; teams: Team[]; proposals: Proposal[]; onBack: () => void; onStatus: (id: string, status: Proposal['status']) => Promise<void>; onCreated: (proposal: Proposal) => void }) { const [idea, setIdea] = useState(''); const [plan, setPlan] = useState(''); const [deadline, setDeadline] = useState(''); const [link, setLink] = useState(''); const [teamId, setTeamId] = useState(teams[0]?.id || ''); async function submit() { if (!task || !teamId) return; const created = await api<Proposal>('/proposals', { method: 'POST', body: JSON.stringify({ task_id: task.id, team_id: teamId, idea, plan, deadline, prototype_link: link }) }); onCreated(created); setIdea(''); setPlan(''); setDeadline(''); setLink(''); } return <div className="detail-layout">{task && <section className="detail-main"><button className="back-link" onClick={onBack}>← Назад в каталог</button><span className="pill">{task.status} · {task.rating_total}/100</span><h2>{task.title}</h2><p className="lead">{task.context_and_need}</p><Info title="Что нужно получить" value={task.expected_result} /><Info title="Критерии успеха" value={task.success_criteria} /><Info title="Ограничения" value={task.limitations} /><RatingWidget rating_total={task.rating_total} status={task.status} rating_breakdown={task.rating_breakdown} missing_fields={task.missing_fields} /></section>}<aside className="detail-side">{role === 'freelancer' && task && <div className="form-card"><h3>Предложить решение</h3><p className="muted">Команда отправит предложение бизнесу на ручное рассмотрение.</p><select value={teamId} onChange={(event) => setTeamId(event.target.value)}>{teams.map((team) => <option key={team.id} value={team.id}>{team.name}</option>)}</select><textarea placeholder="Идея решения" value={idea} onChange={(event) => setIdea(event.target.value)} /><textarea placeholder="План работ" value={plan} onChange={(event) => setPlan(event.target.value)} /><input placeholder="Deadline" value={deadline} onChange={(event) => setDeadline(event.target.value)} /><input placeholder="Prototype link" value={link} onChange={(event) => setLink(event.target.value)} /><button className="primary-button full" disabled={!idea || !plan || !deadline} onClick={() => void submit()}>Отправить предложение</button></div>}{proposals.map((proposal) => <article className="proposal-card" key={proposal.id}><div className="proposal-head"><b>{teams.find((team) => team.id === proposal.team_id)?.name || 'Команда'}</b><span className={`status ${proposal.status}`}>{proposal.status}</span></div><h4>{proposal.idea}</h4><p>{proposal.plan}</p><small>Deadline: {proposal.deadline}</small>{role === 'business' && <div className="actions"><button className="accept" onClick={() => void onStatus(proposal.id, 'accepted')}>Accept</button><button className="reject" onClick={() => void onStatus(proposal.id, 'rejected')}>Reject</button></div>}</article>)}</aside></div>; }
function Info({ title, value }: { title: string; value: string }) { return <div className="info-block"><small>{title}</small><p>{value || 'Пока не указано'}</p></div>; }
function ProjectsView({ proposals, tasks }: { proposals: Proposal[]; tasks: Task[] }) {
  return <div className="project-list">{proposals.length ? proposals.map((proposal) => <article className="proposal-card" key={proposal.id}><span className="status accepted">Принято</span><h3>{tasks.find((task) => task.id === proposal.task_id)?.title || 'Проект'}</h3><p>{proposal.idea}</p><small>Срок: {proposal.deadline}</small></article>) : <div className="empty-state">Пока нет принятых проектов. Посмотрите задачи в каталоге и отправьте предложение.</div>}</div>;
}

function ProfileView({ profile, role, proposals, onSave }: { profile: Profile; role: Role; proposals: Proposal[]; onSave: (changes: ProfileChanges) => Promise<Profile> }) {
  const [edit, setEdit] = useState(false);
  const [draft, setDraft] = useState(profile);
  const [saveState, setSaveState] = useState<'idle' | 'saving' | 'saved' | 'error'>('idle');
  const [saveError, setSaveError] = useState('');
  useEffect(() => { setDraft(profile); setEdit(false); setSaveState('idle'); setSaveError(''); }, [profile.id]);

  function change(patch: Partial<Profile>) {
    setDraft((current) => ({ ...current, ...patch }));
    setSaveState('idle');
    setSaveError('');
  }

  async function save() {
    setSaveState('saving');
    setSaveError('');
    try {
      const { name, company, headline, description, industry, skills, experience, city, contacts, avatar } = draft;
      const updated = await onSave({ name, company, headline, description, industry, skills, experience, city, contacts, avatar });
      setDraft(updated);
      setSaveState('saved');
    } catch (cause) {
      setSaveState('error');
      setSaveError(cause instanceof Error ? cause.message : String(cause));
    }
  }

  return <div className="profile-layout">
    <section className="profile-hero">
      <div className="profile-avatar">{profile.name.slice(0, 1)}</div>
      <div><span className="pill">DEMO · {role === 'business' ? 'Бизнес' : 'Фрилансер'}</span><h2>{role === 'business' ? profile.company : profile.name}</h2><p>{role === 'business' ? profile.name : profile.headline}</p><span className="muted">{profile.city}</span></div>
      <button className="secondary-button" type="button" onClick={() => { setEdit(!edit); setDraft(profile); setSaveState('idle'); setSaveError(''); }} disabled={saveState === 'saving'}>{edit ? 'Отменить' : 'Редактировать'}</button>
    </section>
    {edit ? <section className="form-card profile-form">
      <label>Имя<input value={draft.name} onChange={(e) => change({ name: e.target.value })} /></label>
      {role === 'business' ? <>
        <label>Компания<input value={draft.company} onChange={(e) => change({ company: e.target.value })} /></label>
        <label>Отрасль<input value={draft.industry} onChange={(e) => change({ industry: e.target.value })} /></label>
      </> : <>
        <label>Специализация<input value={draft.headline} onChange={(e) => change({ headline: e.target.value })} /></label>
        <label>Навыки<input value={draft.skills.join(', ')} onChange={(e) => change({ skills: e.target.value.split(',').map((s) => s.trim()).filter(Boolean) })} /></label>
        <label>Опыт<input value={draft.experience} onChange={(e) => change({ experience: e.target.value })} /></label>
      </>}
      <label>Город<input value={draft.city} onChange={(e) => change({ city: e.target.value })} /></label>
      <label>Email<input type="email" value={draft.contacts.email || ''} onChange={(e) => change({ contacts: { ...draft.contacts, email: e.target.value } })} /></label>
      <label>Телефон<input value={draft.contacts.phone || ''} onChange={(e) => change({ contacts: { ...draft.contacts, phone: e.target.value } })} /></label>
      <label>Описание<textarea value={draft.description} onChange={(e) => change({ description: e.target.value })} /></label>
      <div className="profile-save-row"><button className="primary-button" type="button" disabled={saveState === 'saving' || saveState === 'saved'} onClick={() => void save()}>{saveState === 'saving' ? 'Сохранение…' : saveState === 'saved' ? 'Сохранено' : 'Сохранить изменения'}</button>
        {saveState === 'saved' && <span className="save-success" role="status">Изменения сохранены</span>}
      </div>
      {saveState === 'error' && <div className="alert" role="alert"><b>Не удалось сохранить изменения.</b><br />{saveError}</div>}
    </section> : <section className="profile-details"><Info title="Описание" value={profile.description} /><Info title="Город" value={profile.city} /><Info title="Контакт" value={Object.values(profile.contacts).filter(Boolean).join(' · ')} />{role === 'business' ? <Info title="Отрасль" value={profile.industry} /> : <><Info title="Навыки" value={profile.skills.join(' · ')} /><Info title="Опыт" value={profile.experience} /><Info title="Отклики" value={String(proposals.length) + ' всего · ' + String(proposals.filter((p) => p.status === 'accepted').length) + ' приняты'} /></>}</section>}
  </div>;
}
