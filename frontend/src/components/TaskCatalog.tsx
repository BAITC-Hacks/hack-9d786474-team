import { useMemo, useState } from 'react';
import type { Task, TaskStatus } from './TaskBuilder';

type StatusFilter = TaskStatus | 'all';

export type TaskCatalogProps = {
  /** Pass only tasks that are visible in the public catalog. */
  tasks: Task[];
  /** Local UI metadata; tags do not extend the backend Task contract. */
  tagsByTaskId?: Record<string, string[]>;
  onViewAndRespond: (task: Task) => void;
};

const STATUS_LABELS: Record<TaskStatus, string> = {
  draft: 'Черновик',
  working: 'Рабочая',
  ready: 'Готовая',
  priority: 'Приоритетная',
};

const STATUS_ORDER: Record<TaskStatus, number> = {
  priority: 0,
  ready: 1,
  working: 2,
  draft: 3,
};

const STATUS_BADGES: Record<TaskStatus, string> = {
  draft: 'bg-slate-100 text-slate-700 ring-slate-200',
  working: 'bg-amber-50 text-amber-800 ring-amber-200',
  ready: 'bg-emerald-50 text-emerald-700 ring-emerald-200',
  priority: 'bg-violet-50 text-violet-700 ring-violet-200',
};

function getContextPreview(context: string, limit = 180) {
  const normalized = context.trim().replace(/\\s+/g, ' ');
  return normalized.length > limit ? normalized.slice(0, limit).trimEnd() + '…' : normalized;
}

export function TaskCatalog({ tasks, tagsByTaskId = {}, onViewAndRespond }: TaskCatalogProps) {
  const [statusFilter, setStatusFilter] = useState<StatusFilter>('all');
  const [tagFilter, setTagFilter] = useState('all');

  const availableTags = useMemo(
    () => [...new Set(Object.values(tagsByTaskId).flat())].sort((left, right) => left.localeCompare(right, 'ru')),
    [tagsByTaskId],
  );

  const visibleTasks = useMemo(
    () =>
      tasks
        .filter((task) => statusFilter === 'all' || task.status === statusFilter)
        .filter((task) => tagFilter === 'all' || (tagsByTaskId[task.id] ?? []).includes(tagFilter))
        .sort((left, right) => {
          const statusDifference = STATUS_ORDER[left.status] - STATUS_ORDER[right.status];
          return statusDifference || right.rating_total - left.rating_total;
        }),
    [tasks, statusFilter, tagFilter, tagsByTaskId],
  );

  return (
    <main className="mx-auto w-full max-w-6xl px-4 py-8 sm:px-6 lg:px-8">
      <header className="flex flex-col gap-2">
        <p className="text-sm font-semibold uppercase tracking-wide text-indigo-600">Каталог</p>
        <h1 className="text-3xl font-bold tracking-tight text-slate-900">Задачи для команд</h1>
        <p className="max-w-2xl text-slate-600">Выберите бизнес-задачу и предложите команде план решения.</p>
      </header>

      <section aria-label="Фильтры каталога" className="mt-6 flex flex-col gap-4 rounded-2xl border border-slate-200 bg-white p-4 sm:flex-row sm:items-end">
        <div className="w-full sm:max-w-xs">
          <label htmlFor="catalog-status" className="block text-sm font-medium text-slate-700">Уровень готовности</label>
          <select
            id="catalog-status"
            value={statusFilter}
            onChange={(event) => setStatusFilter(event.target.value as StatusFilter)}
            className="mt-1 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-slate-900 shadow-sm outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200"
          >
            <option value="all">Все уровни</option>
            <option value="draft">Черновик</option>
            <option value="working">Рабочая</option>
            <option value="ready">Готовая</option>
            <option value="priority">Приоритетная</option>
          </select>
        </div>

        <div className="w-full sm:max-w-xs">
          <label htmlFor="catalog-tag" className="block text-sm font-medium text-slate-700">Отрасль или тег</label>
          <select
            id="catalog-tag"
            value={tagFilter}
            onChange={(event) => setTagFilter(event.target.value)}
            className="mt-1 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-slate-900 shadow-sm outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200"
          >
            <option value="all">Все отрасли и теги</option>
            {availableTags.map((tag) => <option key={tag} value={tag}>{tag}</option>)}
          </select>
        </div>

        <p className="text-sm text-slate-500 sm:ml-auto" aria-live="polite">Найдено задач: {visibleTasks.length}</p>
      </section>

      {visibleTasks.length === 0 ? (
        <div className="mt-6 rounded-2xl border border-dashed border-slate-300 bg-slate-50 px-6 py-12 text-center">
          <h2 className="font-semibold text-slate-900">Подходящих задач пока нет</h2>
          <p className="mt-1 text-sm text-slate-600">Измените фильтры или загляните позже.</p>
        </div>
      ) : (
        <ul className="mt-6 grid gap-4 lg:grid-cols-2">
          {visibleTasks.map((task) => {
            const tags = tagsByTaskId[task.id] ?? [];
            return (
              <li key={task.id} className="flex flex-col rounded-2xl border border-slate-200 bg-white p-5 shadow-sm transition hover:border-indigo-200 hover:shadow-md">
                <div className="flex flex-wrap items-start justify-between gap-3">
                  <h2 className="text-lg font-semibold leading-6 text-slate-900">{task.title}</h2>
                  <div className="flex shrink-0 items-center gap-2">
                    <span className="text-sm font-bold tabular-nums text-slate-900">{task.rating_total}/100</span>
                    <span className={'rounded-full px-2.5 py-1 text-xs font-semibold ring-1 ring-inset ' + STATUS_BADGES[task.status]}>
                      {STATUS_LABELS[task.status]}
                    </span>
                  </div>
                </div>

                <p className="mt-3 line-clamp-3 text-sm leading-6 text-slate-600">
                  {getContextPreview(task.context_and_need) || 'Описание контекста пока не добавлено.'}
                </p>

                {tags.length > 0 && (
                  <ul aria-label="Отрасли и теги" className="mt-4 flex flex-wrap gap-2">
                    {tags.map((tag) => (
                      <li key={tag} className="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-medium text-slate-600">{tag}</li>
                    ))}
                  </ul>
                )}

                <button
                  type="button"
                  onClick={() => onViewAndRespond(task)}
                  className="mt-5 inline-flex w-full items-center justify-center rounded-lg bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-indigo-700 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500 focus-visible:ring-offset-2 sm:w-auto sm:self-start"
                >
                  Посмотреть и откликнуться
                </button>
              </li>
            );
          })}
        </ul>
      )}
    </main>
  );
}
