import json
import os
from openai import OpenAI
from .schemas import CARD_FIELDS, UNKNOWN_VALUE, Stage1Result, TaskField

class AIServiceError(RuntimeError):
    """Expected failure while calling or validating the external AI service."""

STAGE1_SYSTEM_PROMPT = """Ты — ассистент платформы геймификации бизнес-задач для студентов.
Твоя цель — помочь представителю бизнеса превратить сырое описание потребности в четкое ТЗ.

Анализируй текст пользователя по следующим 7 критериям:

1. Контекст и потребность (что происходит и зачем менять)
2. Данные и материалы (доступные данные, API, документы)
3. Ожидаемый результат (конкретный продукт/фича)
4. Критерии успеха (метрики, измеримый результат)
5. Ограничения (сроки, технологии, условия)
6. Целевые пользователи (кто будет пользоваться)
7. Контакт и формат связи (кто отвечает, как проходят созвоны)

СТРОГИЕ ПРАВИЛА:

1. Задай МИНИМУМ 3 и МАКСИМУМ 5 уточняющих вопросов по тем полям,
о которых в черновике нет сведений или они описаны слишком размыто.
2. НЕ ПРИДУМЫВАЙ и НЕ ДОБАВЛЯЙ факты, которых пользователь не сообщал.
3. Вопросы должны быть вежливыми, конкретными и простыми для ответа бизнесом.
4. Ответ ВСЕГДА отдавай строго в формате JSON без каких-либо вводных слов или Markdown-оберток.

Схема ответа JSON:
{
"analyzed_draft": "Краткое резюме того, что уже понятно из черновика",
"missing_aspects": ["list_of_missing_field_names"],
"questions": [
{"id": "q1", "target_field": "data_and_materials", "question": "..."},
{"id": "q2", "target_field": "success_criteria", "question": "..."},
{"id": "q3", "target_field": "business_contact", "question": "..."}
]
}"""

STAGE2_SYSTEM_PROMPT = """Ты — эксперт по структурированию бизнес-требований. Твоя задача —
объединить первоначальный черновик задачи и ответы представителя бизнеса на уточняющие
вопросы в единую структурированную карточку.

СТРОГИЕ ПРАВИЛА:

1. Заполни все поля и сгенерируй емкое название задачи (title).
2. Используй ТОЛЬКО ту информацию, которую явно предоставил пользователь в черновике или ответах.
3. Если по какому-то полю пользователь так и не предоставил информации, напиши в значении этого поля:
"Не указано (требуется уточнение)". НЕ ПРИДУМЫВАЙ контакты, датасеты или метрики!
4. Ответ отдавай СТРОГО в формате JSON.

Схема ответа JSON:
{
"title": "...",
"context_and_need": "...",
"data_and_materials": "... или 'Не указано (требуется уточнение)'",
"expected_result": "...",
"success_criteria": "... или 'Не указано (требуется уточнение)'",
"limitations": "... или 'Не указано (требуется уточнение)'",
"target_users": "...",
"business_contact": "... или 'Не указано (требуется уточнение)'",
"interaction_format": "... или 'Не указано (требуется уточнение)'"
}"""

def _stub(draft: str) -> dict:
    return {
        "analyzed_draft": draft[:500],
        "missing_aspects": ["data_and_materials", "success_criteria", "business_contact", "interaction_format"],
        "questions": [
            {"id": "q1", "target_field": "data_and_materials", "question": "Какие данные, документы или API доступны команде?"},
            {"id": "q2", "target_field": "success_criteria", "question": "По каким измеримым признакам вы поймёте, что результат успешен?"},
            {"id": "q3", "target_field": "business_contact", "question": "Кто будет контактным лицом со стороны бизнеса?"},
        ],
    }

def analyze_draft(draft: str) -> dict:
    if os.getenv("USE_AI_STUB", "true").lower() == "true":
        return _stub(draft)
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY не задан при USE_AI_STUB=false")
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        temperature=0,
        response_format={"type": "json_object"},
        messages=[{"role": "system", "content": STAGE1_SYSTEM_PROMPT}, {"role": "user", "content": draft}],
    )
    raw = response.choices[0].message.content or ""
    try:
        return Stage1Result.model_validate_json(raw).model_dump()
    except Exception as exc:
        raise ValueError(f"AI вернул невалидный JSON stage 1: {exc}") from exc

def assemble_card(draft: str, answers: dict[str, str]) -> dict:
    if os.getenv("USE_AI_STUB", "true").lower() == "true":
        fields = {key: answers.get(key, "Не указано (требуется уточнение)") for key in (
            "data_and_materials", "success_criteria", "business_contact", "interaction_format")}
        return {"title": draft[:100], "context_and_need": draft, "expected_result": "Не указано (требуется уточнение)",
                "limitations": "Не указано (требуется уточнение)", "target_users": "Не указано (требуется уточнение)", **fields}
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY не задан при USE_AI_STUB=false")
    client = OpenAI(api_key=api_key)
    payload = json.dumps({"draft": draft, "answers": answers}, ensure_ascii=False)
    response = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"), temperature=0,
        response_format={"type": "json_object"},
        messages=[{"role": "system", "content": STAGE2_SYSTEM_PROMPT}, {"role": "user", "content": payload}],
    )
    raw = response.choices[0].message.content or ""
    try:
        data = json.loads(raw)
        required = ["title", "context_and_need", "data_and_materials", "expected_result", "success_criteria",
                    "limitations", "target_users", "business_contact", "interaction_format"]
        if any(key not in data for key in required):
            raise ValueError("отсутствуют обязательные поля")
        return data
    except Exception as exc:
        raise ValueError(f"AI вернул невалидный JSON stage 2: {exc}") from exc
