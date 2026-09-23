type TaskStatus = 'draft' | 'working' | 'ready' | 'priority';

export type RatingWidgetProps = {
  rating_total: number;
  status: TaskStatus;
  rating_breakdown: Record<string, number>;
  missing_fields: string[];
};

const STATUS_LABELS: Record<TaskStatus, string> = {
  draft: 'Черновик',
  working: 'Рабочая',
  ready: 'Готовая',
  priority: 'Приоритетная',
};

const FIELD_META: Record<string, { label: string; weight: number }> = {
  context_and_need: { label: 'Контекст и потребность', weight: 20 },
  data_and_materials: { label: 'Данные и материалы', weight: 20 },
  expected_result: { label: 'Ожидаемый результат', weight: 15 },
  success_criteria: { label: 'Критерии успеха', weight: 15 },
  limitations: { label: 'Ограничения', weight: 10 },
  target_users: { label: 'Целевые пользователи', weight: 10 },
  business_contact_and_interaction_format: {
    label: 'Контакт со стороны бизнеса и формат взаимодействия',
    weight: 10,
  },
};

const COLOR_STYLES = {
  red: {
    bar: 'bg-red-500',
    badge: 'bg-red-50 text-red-700 ring-red-200',
  },
  yellow: {
    bar: 'bg-amber-400',
    badge: 'bg-amber-50 text-amber-800 ring-amber-200',
  },
  green: {
    bar: 'bg-emerald-500',
    badge: 'bg-emerald-50 text-emerald-700 ring-emerald-200',
  },
  purple: {
    bar: 'bg-violet-600',
    badge: 'bg-violet-50 text-violet-700 ring-violet-200',
  },
};

function getColor(score: number) {
  if (score >= 90) return COLOR_STYLES.purple;
  if (score >= 70) return COLOR_STYLES.green;
  if (score >= 40) return COLOR_STYLES.yellow;
  return COLOR_STYLES.red;
}

function InfoIcon() {
  return (
    <svg aria-hidden="true" viewBox="0 0 20 20" fill="currentColor" className="mt-0.5 h-5 w-5 shrink-0 text-blue-600">
      <path
        fillRule="evenodd"
        d="M18 10a8 8 0 1 1-16 0 8 8 0 0 1 16 0ZM9 8.75a1 1 0 1 1 2 0v5a1 1 0 0 1-2 0v-5ZM10 5a1 1 0 1 0 0 2 1 1 0 0 0 0-2Z"
        clipRule="evenodd"
      />
    </svg>
  );
}

export function RatingWidget({
  rating_total,
  status,
  rating_breakdown,
  missing_fields,
}: RatingWidgetProps) {
  const color = getColor(rating_total);
  const progress = Math.min(100, Math.max(0, rating_total));
  const knownMissingFields = missing_fields.filter((field) => FIELD_META[field]);

  return (
    <section aria-labelledby="task-rating-title" className="w-full max-w-2xl rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="text-sm font-medium text-slate-500">Готовность задачи</p>
          <h2 id="task-rating-title" className="mt-1 text-3xl font-bold tracking-tight text-slate-900">
            {rating_total}<span className="ml-1 text-lg font-semibold text-slate-500">/ 100</span>
          </h2>
        </div>
        <span className={`inline-flex rounded-full px-3 py-1.5 text-sm font-semibold ring-1 ring-inset ${color.badge}`}>
          {STATUS_LABELS[status]}
        </span>
      </div>

      <div className="mt-5 h-4 overflow-hidden rounded-full bg-slate-100" role="progressbar" aria-label="Рейтинг готовности задачи" aria-valuemin={0} aria-valuemax={100} aria-valuenow={progress}>
        <div className={`h-full rounded-full transition-[width] duration-500 ${color.bar}`} style={{ width: `${progress}%` }} />
      </div>
      <div className="mt-1 flex justify-between text-xs text-slate-400" aria-hidden="true"><span>0</span><span>100</span></div>

      <details className="mt-6 border-t border-slate-200 pt-4">
        <summary className="cursor-pointer list-none font-semibold text-slate-800 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500">
          <span className="flex items-center justify-between">
            <span>Детализация рейтинга</span>
            <span className="text-sm font-medium text-slate-500">{Object.keys(rating_breakdown).length} полей</span>
          </span>
        </summary>
        <ul className="mt-4 space-y-3">
          {Object.entries(rating_breakdown).map(([field, points]) => {
            const meta = FIELD_META[field];
            return (
              <li key={field} className="flex items-center justify-between gap-4 text-sm">
                <span className="text-slate-700">{meta?.label ?? field}</span>
                <span className={`shrink-0 font-semibold tabular-nums ${points > 0 ? 'text-slate-900' : 'text-slate-400'}`}>
                  {points}{meta ? ` / ${meta.weight}` : ''} баллов
                </span>
              </li>
            );
          })}
        </ul>
      </details>

      {knownMissingFields.length > 0 && (
        <div className="mt-5 rounded-xl bg-blue-50/70 p-4">
          <h3 className="font-semibold text-slate-900">Как повысить рейтинг</h3>
          <ul className="mt-3 space-y-3">
            {knownMissingFields.map((field) => {
              const meta = FIELD_META[field];
              return (
                <li key={field} className="flex items-start gap-2 text-sm leading-5 text-slate-700">
                  <InfoIcon />
                  <span>Добавьте «{meta.label.toLowerCase()}», чтобы получить +{meta.weight} баллов.</span>
                </li>
              );
            })}
          </ul>
        </div>
      )}
    </section>
  );
}
