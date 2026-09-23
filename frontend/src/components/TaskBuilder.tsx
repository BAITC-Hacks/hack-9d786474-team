import { useState } from 'react';

type TaskStatus = 'draft' | 'working' | 'ready' | 'priority';

type Stage1Question = {
  id: string;
  target_field: string;
  question: string;
};

type Task = {
  id: string;
  title: string;
  context_and_need: string;
  data_and_materials: string;
  expected_result: string;
  success_criteria: string;
  limitations: string;
  target_users: string;
  business_contact: string;
  interaction_format: string;
  status: TaskStatus;
  rating_total: number;
  rating_breakdown: Record<string, number>;
  missing_fields: string[];
  stage1_result: {
    analyzed_draft: string;
    missing_aspects: string[];
    questions: Stage1Question[];
  };
};

type TaskFields = Pick<
  Task,
  | 'title'
  | 'context_and_need'
  | 'data_and_materials'
  | 'expected_result'
  | 'success_criteria'
  | 'limitations'
  | 'target_users'
  | 'business_contact'
  | 'interaction_format'
>;

type TaskBuilderProps = {
  onConfirm: (task: Task) => void | Promise<void>;
};

const EMPTY_FIELDS: TaskFields = {
  title: '',
  context_and_need: '',
  data_and_materials: '',
  expected_result: '',
  success_criteria: '',
  limitations: '',
  target_users: '',
  business_contact: '',
  interaction_format: '',
};

const FIELD_LABELS: { key: keyof TaskFields; label: string }[] = [
  { key: 'title', label: 'Название задачи' },
  { key: 'context_and_need', label: 'Контекст и потребность' },
  { key: 'data_and_materials', label: 'Данные и материалы' },
  { key: 'expected_result', label: 'Ожидаемый результат' },
  { key: 'success_criteria', label: 'Критерии успеха' },
  { key: 'limitations', label: 'Ограничения' },
  { key: 'target_users', label: 'Целевые пользователи' },
  { key: 'business_contact', label: 'Контакт со стороны бизнеса' },
  { key: 'interaction_format', label: 'Формат взаимодействия' },
];

export function TaskBuilder({ onConfirm }: TaskBuilderProps) {
  const [rawText, setRawText] = useState('');
  const [taskId, setTaskId] = useState<string | null>(null);
  const [task, setTask] = useState<Task | null>(null);
  const [questions, setQuestions] = useState<Stage1Question[]>([]);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [fields, setFields] = useState<TaskFields>(EMPTY_FIELDS);
  const [stage, setStage] = useState<1 | 2 | 3>(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [confirmed, setConfirmed] = useState(false);

  async function requestJson<T>(url: string, body: unknown): Promise<T> {
    const response = await fetch(url, {
      method: url === '/tasks/draft' ? 'POST' : 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    if (!response.ok) {
      throw new Error('Сервер не смог обработать задачу. Попробуйте ещё раз.');
    }
    return (await response.json()) as T;
  }

  async function createDraft() {
    setLoading(true);
    setError('');
    try {
      const created = await requestJson<Task>('/tasks/draft', { draft_text: rawText.trim() });
      const nextQuestions = created.stage1_result?.questions ?? [];
      setTaskId(created.id);
      setTask(created);
      setFields({
        title: created.title,
        context_and_need: created.context_and_need,
        data_and_materials: created.data_and_materials,
        expected_result: created.expected_result,
        success_criteria: created.success_criteria,
        limitations: created.limitations,
        target_users: created.target_users,
        business_contact: created.business_contact,
        interaction_format: created.interaction_format,
      });
      setQuestions(nextQuestions);
      setAnswers(Object.fromEntries(nextQuestions.map(({ target_field }) => [target_field, ''])));
      setStage(2);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : 'Произошла ошибка. Попробуйте ещё раз.');
    } finally {
      setLoading(false);
    }
  }

  async function submitAnswers() {
    if (!taskId) return;
    setLoading(true);
    setError('');
    try {
      const updated = await requestJson<Task>(`/tasks/${taskId}`, {
        answers,
        confirmed: false,
      });
      setTask(updated);
      setFields({
        title: updated.title,
        context_and_need: updated.context_and_need,
        data_and_materials: updated.data_and_materials,
        expected_result: updated.expected_result,
        success_criteria: updated.success_criteria,
        limitations: updated.limitations,
        target_users: updated.target_users,
        business_contact: updated.business_contact,
        interaction_format: updated.interaction_format,
      });
      setStage(3);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : 'Произошла ошибка. Попробуйте ещё раз.');
    } finally {
      setLoading(false);
    }
  }

  async function confirmCard() {
    if (!taskId || !task) return;
    setLoading(true);
    setError('');
    try {
      const updated = await requestJson<Task>(`/tasks/${taskId}`, {
        ...fields,
        confirmed: true,
      });
      setTask(updated);
      setConfirmed(true);
      await onConfirm(updated);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : 'Не удалось сохранить карточку.');
    } finally {
      setLoading(false);
    }
  }

  const inputClass =
    'mt-1 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-slate-900 shadow-sm outline-none transition focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 disabled:bg-slate-100';

  return (
    <section className="mx-auto max-w-3xl space-y-6 rounded-2xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
      <header>
        <p className="text-sm font-semibold text-indigo-600">Конструктор задачи · шаг {stage} из 3</p>
        <h1 className="mt-1 text-2xl font-bold text-slate-900">Опишите бизнес-задачу</h1>
      </header>

      {stage === 1 && (
        <div>
          <label htmlFor="raw-task" className="text-sm font-medium text-slate-800">Черновое описание</label>
          <textarea
            id="raw-task"
            className={`${inputClass} min-h-40 resize-y`}
            value={rawText}
            onChange={(event) => setRawText(event.target.value)}
            placeholder="Расскажите, какую задачу нужно решить, что уже известно и какой результат нужен…"
          />
          <button
            type="button"
            disabled={!rawText.trim() || loading}
            onClick={() => void createDraft()}
            className="mt-4 rounded-lg bg-indigo-600 px-4 py-2.5 font-semibold text-white hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {loading ? 'Анализируем…' : 'Анализировать с AI'}
          </button>
        </div>
      )}

      {stage === 2 && (
        <div className="space-y-4">
          <h2 className="font-semibold text-slate-900">Уточните детали</h2>
          {questions.map((item) => (
            <div key={item.id}>
              <label htmlFor={item.id} className="text-sm font-medium text-slate-800">{item.question}</label>
              <textarea
                id={item.id}
                className={`${inputClass} min-h-20`}
                value={answers[item.target_field] ?? ''}
                onChange={(event) =>
                  setAnswers((current) => ({ ...current, [item.target_field]: event.target.value }))
                }
              />
            </div>
          ))}
          <button
            type="button"
            disabled={loading}
            onClick={() => void submitAnswers()}
            className="rounded-lg bg-indigo-600 px-4 py-2.5 font-semibold text-white hover:bg-indigo-700 disabled:opacity-50"
          >
            {loading ? 'Обновляем…' : 'Обновить карточку'}
          </button>
        </div>
      )}

      {stage === 3 && (
        <div className="space-y-4">
          <h2 className="font-semibold text-slate-900">Проверьте и отредактируйте карточку</h2>
          {FIELD_LABELS.map(({ key, label }) => (
            <div key={key}>
              <label htmlFor={key} className="text-sm font-medium text-slate-800">{label}</label>
              {key === 'title' ? (
                <input
                  id={key}
                  className={inputClass}
                  value={fields[key]}
                  onChange={(event) => setFields((current) => ({ ...current, [key]: event.target.value }))}
                  disabled={confirmed}
                />
              ) : (
                <textarea
                  id={key}
                  className={`${inputClass} min-h-20`}
                  value={fields[key]}
                  onChange={(event) => setFields((current) => ({ ...current, [key]: event.target.value }))}
                  disabled={confirmed}
                />
              )}
            </div>
          ))}
          {task && (
            <p className="text-sm text-slate-600">
              Готовность: {task.rating_total}/100 · статус: {task.status}
            </p>
          )}
          <button
            type="button"
            disabled={confirmed || !fields.title.trim() || loading}
            onClick={() => void confirmCard()}
            className="rounded-lg bg-emerald-600 px-4 py-2.5 font-semibold text-white hover:bg-emerald-700 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {confirmed ? 'Карточка подтверждена' : 'Подтвердить и сохранить карточку'}
          </button>
        </div>
      )}

      {error && <p role="alert" className="rounded-lg bg-red-50 p-3 text-sm text-red-700">{error}</p>}
      {confirmed && <p role="status" className="text-sm text-emerald-700">Карточка подтверждена пользователем.</p>}
    </section>
  );
}
