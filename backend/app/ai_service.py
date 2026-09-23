import json
import os
from openai import OpenAI
from .schemas import CARD_FIELDS, UNKNOWN_VALUE, Stage1Result, TaskField

class AIServiceError(RuntimeError):
    """Expected failure while calling or validating the external AI service."""


def _openai_client(api_key: str) -> OpenAI:
    kwargs = {"api_key": api_key}
    base_url = os.getenv("OPENAI_BASE_URL", "").strip()
    if base_url:
        kwargs["base_url"] = base_url
    return OpenAI(**kwargs)


def _model_name() -> str:
    model = os.getenv("OPENAI_MODEL", "").strip()
    if not model:
        raise AIServiceError("OPENAI_MODEL не задан при USE_AI_STUB=false")
    return model

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

def _call(client: OpenAI, messages: list[dict]) -> str:
    try:
        response_format = {"type": "text"} if os.getenv("OPENAI_BASE_URL", "").strip() else {"type": "json_object"}
        response = client.chat.completions.create(
            model=_model_name(),
            temperature=0,
            response_format=response_format,
            messages=messages,
            timeout=float(os.getenv("OPENAI_TIMEOUT_SECONDS", "30")),
        )
        return response.choices[0].message.content or ""
    except Exception as exc:
        raise AIServiceError(f"Внешний AI недоступен: {exc}") from exc

def analyze_draft(draft: str) -> dict:
    if os.getenv("USE_AI_STUB", "true").lower() == "true":
        return _stub(draft)
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise AIServiceError("OPENAI_API_KEY не задан при USE_AI_STUB=false")
    raw = _call(_openai_client(api_key), [
        {"role": "system", "content": STAGE1_SYSTEM_PROMPT},
        {"role": "user", "content": draft},
    ])
    try:
        return Stage1Result.model_validate_json(raw).model_dump()
    except Exception as exc:
        raise AIServiceError(f"AI вернул невалидный JSON stage 1: {exc}") from exc

def _validate_stage2(raw: str) -> dict:
    try:
        data = json.loads(raw)
    except Exception as exc:
        raise ValueError(f"stage 2 должен содержать валидный JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("stage 2 должен быть JSON-объектом")
    allowed = set(CARD_FIELDS)
    if set(data) != allowed:
        raise ValueError("stage 2 содержит неизвестные или отсутствующие поля")
    for field in CARD_FIELDS:
        value = data[field]
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"поле {field} должно быть непустой строкой")
    if len(data["title"]) > 100:
        raise ValueError("title длиннее 100 символов")
    return data

def assemble_card(draft: str, answers: dict[TaskField, str]) -> dict:
    if os.getenv("USE_AI_STUB", "true").lower() == "true":
        result = {
            "title": draft[:100] or UNKNOWN_VALUE,
            "context_and_need": draft or UNKNOWN_VALUE,
            "data_and_materials": answers.get("data_and_materials", UNKNOWN_VALUE),
            "expected_result": UNKNOWN_VALUE,
            "success_criteria": answers.get("success_criteria", UNKNOWN_VALUE),
            "limitations": UNKNOWN_VALUE,
            "target_users": UNKNOWN_VALUE,
            "business_contact": answers.get("business_contact", UNKNOWN_VALUE),
            "interaction_format": answers.get("interaction_format", UNKNOWN_VALUE),
        }
        return _validate_stage2(json.dumps(result, ensure_ascii=False))
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise AIServiceError("OPENAI_API_KEY не задан при USE_AI_STUB=false")
    payload = json.dumps({"draft": draft, "answers": answers}, ensure_ascii=False)
    raw = _call(_openai_client(api_key), [
        {"role": "system", "content": STAGE2_SYSTEM_PROMPT},
        {"role": "user", "content": payload},
    ])
    try:
        return _validate_stage2(raw)
    except Exception as exc:
        raise AIServiceError(f"AI вернул невалидный JSON stage 2: {exc}") from exc
