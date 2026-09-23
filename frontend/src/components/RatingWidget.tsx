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

// Display metadata only. The backend owns the actual points, total, and status.
const CRITERIA = [
  { key: 'context_and_need', label: 'Контекст и потребность', max: 20 },
  { key: 'data_and_materials', label: 'Данные и материалы', max: 20 },
  { key: 'expected_result', label: 'Ожидаемый результат', max: 15 },
  { key: 'success_criteria', label: 'Критерии успеха', max: 15 },
  { key: 'limitations', label: 'Ограничения', max: 10 },
  { key: 'target_users', label: 'Целевые пользователи', max: 10 },
  { key: 'business_contact_and_interaction_format', label: 'Контакт и формат взаимодействия', max: 10 },
] as const;

export function RatingWidget({ rating_total, status, rating_breakdown, missing_fields }: RatingWidgetProps) {
  const missing = CRITERIA.filter(({ key }) => missing_fields.includes(key));
  return (
    <section className={`rating-panel rating-${status}`} aria-labelledby="task-rating-title">
      <div className="rating-header">
        <div>
          <p className="rating-overline">Готовность</p>
          <h2 id="task-rating-title" className="rating-score">{rating_total}<span> / 100</span></h2>
        </div>
        <span className="rating-status">{STATUS_LABELS[status]}</span>
      </div>
      <div className="rating-overall-track" role="progressbar" aria-label="Общая готовность" aria-valuemin={0} aria-valuemax={100} aria-valuenow={rating_total}>
        <span style={{ width: `${Math.min(100, Math.max(0, rating_total))}%` }} />
      </div>
      <h3 className="rating-subtitle">Детализация</h3>
      <ul className="rating-criteria">
        {CRITERIA.map(({ key, label, max }) => {
          const points = rating_breakdown[key] ?? 0;
          return (
            <li className="rating-criterion" key={key}>
              <div className="rating-criterion-top"><span>{label}</span><strong>{points} / {max}</strong></div>
              <div className="rating-criterion-track" aria-hidden="true">
                <span style={{ width: `${Math.min(100, Math.max(0, points / max * 100))}%` }} />
              </div>
            </li>
          );
        })}
      </ul>
      {missing.length > 0 && (
        <p className="rating-hint">Для повышения готовности уточните: {missing.map(({ label }) => label.toLowerCase()).join(', ')}.</p>
      )}
    </section>
  );
}
