import type { TaskCard } from '../types';

export type TaskRating = {
  totalScore: number;
  status: TaskCard['status'];
  breakdown: Record<string, number>;
  missingFieldsRecommendations: string[];
};

const RATING_FIELDS = [
  {
    key: 'contextAndNeed',
    points: 20,
    label: 'контекст и потребность',
    isComplete: (value: string) => value.trim().length > 15,
  },
  {
    key: 'dataAndMaterials',
    points: 20,
    label: 'данные и материалы',
  },
  {
    key: 'expectedResult',
    points: 15,
    label: 'ожидаемый результат',
  },
  {
    key: 'successCriteria',
    points: 15,
    label: 'критерии успеха',
  },
  {
    key: 'constraints',
    points: 10,
    label: 'ограничения',
  },
  {
    key: 'users',
    points: 10,
    label: 'пользователей',
  },
  {
    key: 'businessContact',
    points: 10,
    label: 'контакт со стороны бизнеса',
  },
] as const;

export function calculateTaskRating(card: TaskCard): TaskRating {
  const breakdown: Record<string, number> = {};
  const missingFieldsRecommendations: string[] = [];
  let totalScore = 0;

  for (const field of RATING_FIELDS) {
    const value = card[field.key];
    const isComplete =
      'isComplete' in field
        ? field.isComplete(value)
        : value.trim().length > 0;
    const earnedPoints = isComplete ? field.points : 0;

    breakdown[field.key] = earnedPoints;
    totalScore += earnedPoints;

    if (!isComplete) {
      missingFieldsRecommendations.push(
        `Добавьте ${field.label}, чтобы получить +${field.points} баллов`,
      );
    }
  }

  const status: TaskCard['status'] =
    totalScore >= 90
      ? 'priority'
      : totalScore >= 70
        ? 'ready'
        : totalScore >= 40
          ? 'workable'
          : 'draft';

  return {
    totalScore,
    status,
    breakdown,
    missingFieldsRecommendations,
  };
}
