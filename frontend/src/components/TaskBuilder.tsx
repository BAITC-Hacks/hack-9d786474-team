import { useState } from 'react';

type TaskFields = {
  contextAndNeed: string;
  dataAndMaterials: string;
  expectedResult: string;
  successCriteria: string;
  constraints: string;
  users: string;
  businessContact: string;
};

export type TaskCard = TaskFields & {
  id: string;
  title: string;
  score: number;
  status: 'draft' | 'workable' | 'ready' | 'priority';
  isConfirmed: boolean;
};

type ProcessDraftResponse = {
  extractedFields: Partial<TaskFields>;
  clarifyingQuestions: [string, string, string];
};

type TaskBuilderProps = {
  onConfirm: (card: TaskCard) => void | Promise<void>;
  endpoint?: string;
};

const EMPTY_FIELDS: TaskFields = {
  contextAndNeed: '',
  dataAndMaterials: '',
  expectedResult: '',
  successCriteria: '',
  constraints: '',
  users: '',
  businessContact: '',
};

const FIELD_LABELS: { key: keyof TaskFields; label: string }[] = [
  { key: 'contextAndNeed', label: 'Контекст и потребность' },
  { key: 'dataAndMaterials', label: 'Данные и материалы' },
  { key: 'expectedResult', label: 'Ожидаемый результат' },
  { key: 'successCriteria', label: 'Критерии успеха' },
  { key: 'constraints', label: 'Ограничения' },
  { key: 'users', label: 'Пользователи' },
  { key: 'businessContact', label: 'Контакт со стороны бизнеса' },
];

export function TaskBuilder({
  onConfirm,
  endpoint = '/ai/process-draft',
}: TaskBuilderProps) {
  const [rawText, setRawText] = useState('');
  const [questions, setQuestions] = useState<string[]>([]);
  const [answers, setAnswers] = useState<string[]>(['', '', '']);
  const [fields, setFields] = useState<TaskFields>(EMPTY_FIELDS);
  const [title, setTitle] = useState('');
  const [stage, setStage] = useState<1 | 2 | 3>(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [confirmed, setConfirmed] = useState(false);

  async function processDraft(includeAnswers: boolean) {
    setLoading(true);
    setError('');
    try {
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          rawText,
          answers: includeAnswers
            ? Object.fromEntries(
                questions.map((question, index) => [question, answers[index]]),
              )
            : {},
        }),
      });
      if (!response.ok) throw new Error('Сервер не смог обработать описание. Попробуйте ещё раз.');
      const result = (await response.json()) as ProcessDraftResponse;
      setFields((current) => ({ ...current, ...result.extractedFields }));
      if (!includeAnswers) {
        setQuestions(result.clarifyingQuestions);
        setAnswers(['', '', '']);
        setStage(2);
      } else {
        setStage(3);
      }
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : 'Произошла ошибка. Попробуйте ещё раз.');
    } finally {
      setLoading(false);
    }
  }

  async function confirmCard() {
    const card: TaskCard = {
      id: globalThis.crypto?.randomUUID?.() ?? `${Date.now()}`,
      title: title.trim(),
      ...fields,
      score: 0,
      status: 'draft',
      isConfirmed: true,
    };
    await onConfirm(card);
    setConfirmed(true);
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
          <label htmlFor="raw-task" className="text-sm font-medium text-slate-800">
            Черновое описание
          </label>
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
            onClick={() => void processDraft(false)}
            className="mt-4 rounded-lg bg-indigo-600 px-4 py-2.5 font-semibold text-white hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {loading ? 'Анализируем…' : 'Анализировать с AI'}
          </button>
        </div>
      )}

      {stage === 2 && (
        <div className="space-y-4">
          <h2 className="font-semibold text-slate-900">Уточните детали</h2>
          {questions.map((question, index) => (
            <div key={`${index}-${question}`}>
              <label htmlFor={`answer-${index}`} className="text-sm font-medium text-slate-800">
                {question}
              </label>
              <textarea
                id={`answer-${index}`}
                className={`${inputClass} min-h-20`}
                value={answers[index] ?? ''}
                onChange={(event) =>
                  setAnswers((current) =>
                    current.map((answer, answerIndex) =>
                      answerIndex === index ? event.target.value : answer,
                    ),
                  )
                }
              />
            </div>
          ))}
          <button
            type="button"
            disabled={loading}
            onClick={() => void processDraft(true)}
            className="rounded-lg bg-indigo-600 px-4 py-2.5 font-semibold text-white hover:bg-indigo-700 disabled:opacity-50"
          >
            {loading ? 'Обновляем…' : 'Обновить карточку'}
          </button>
        </div>
      )}

      {stage === 3 && (
        <div className="space-y-4">
          <h2 className="font-semibold text-slate-900">Проверьте и отредактируйте карточку</h2>
          <div>
            <label htmlFor="task-title" className="text-sm font-medium text-slate-800">Название задачи</label>
            <input
              id="task-title"
              className={inputClass}
              value={title}
              onChange={(event) => setTitle(event.target.value)}
              disabled={confirmed}
            />
          </div>
          {FIELD_LABELS.map(({ key, label }) => (
            <div key={key}>
              <label htmlFor={key} className="text-sm font-medium text-slate-800">{label}</label>
              <textarea
                id={key}
                className={`${inputClass} min-h-20`}
                value={fields[key]}
                onChange={(event) =>
                  setFields((current) => ({ ...current, [key]: event.target.value }))
                }
                disabled={confirmed}
              />
            </div>
          ))}
          <button
            type="button"
            disabled={confirmed || !title.trim() || loading}
            onClick={() => void confirmCard()}
            className="rounded-lg bg-emerald-600 px-4 py-2.5 font-semibold text-white hover:bg-emerald-700 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {confirmed ? 'Карточка подтверждена' : 'Подтвердить и зафиксировать карточку'}
          </button>
        </div>
      )}

      {error && <p role="alert" className="rounded-lg bg-red-50 p-3 text-sm text-red-700">{error}</p>}
      {confirmed && <p role="status" className="text-sm text-emerald-700">Карточка передана приложению.</p>}
    </section>
  );
}

