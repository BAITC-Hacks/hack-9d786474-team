import json
import logging
import os
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ai", tags=["ai"])

FIELD_NAMES = (
    "contextAndNeed",
    "dataAndMaterials",
    "expectedResult",
    "successCriteria",
    "constraints",
    "users",
    "businessContact",
)

SYSTEM_PROMPT = """Ты помогаешь бизнес-пользователю оформить описание задачи.
Верни строго JSON с ключами extractedFields и clarifyingQuestions.
extractedFields — объект ровно с полями contextAndNeed, dataAndMaterials,
expectedResult, successCriteria, constraints, users, businessContact.
Заполняй поле только фактами, явно указанными в черновике или ответах пользователя.
Если данных нет, значение должно быть пустой строкой. Ничего не выдумывай.
clarifyingQuestions — массив ровно из 3 коротких уточняющих вопросов на русском,
которые в первую очередь закрывают незаполненные поля. Даже если все поля заполнены,
задай три полезных вопроса для проверки требований."""


class ProcessDraftRequest(BaseModel):
    rawText: str = Field(min_length=1, max_length=12000)
    answers: dict[str, str] = Field(default_factory=dict)


class ProcessDraftResponse(BaseModel):
    extractedFields: dict[str, str]
    clarifyingQuestions: list[str] = Field(min_length=3, max_length=3)


def _fallback() -> ProcessDraftResponse:
    return ProcessDraftResponse(
        extractedFields={name: "" for name in FIELD_NAMES},
        clarifyingQuestions=[
            "Какую бизнес-потребность или проблему нужно решить?",
            "Какие данные и материалы доступны, и какие есть ограничения?",
            "Какой результат будет считаться успешным и кто будет им пользоваться?",
        ],
    )


def processDraftWithAI(
    rawText: str, answers: dict[str, str] | None = None
) -> ProcessDraftResponse:
    """Extract explicit facts and return exactly three questions; safely fall back on errors."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return _fallback()

    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        payload = json.dumps(
            {"rawText": rawText, "answers": answers or {}},
            ensure_ascii=False,
        )
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            temperature=0,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": payload},
            ],
        )
        content = response.choices[0].message.content or ""
        data: Any = json.loads(content)
        fields = data.get("extractedFields")
        questions = data.get("clarifyingQuestions")
        if not isinstance(fields, dict) or not isinstance(questions, list):
            raise ValueError("Unexpected AI response shape")

        normalized_fields = {
            name: value if isinstance(value, str) else ""
            for name in FIELD_NAMES
            for value in [fields.get(name, "")]
        }
        normalized_questions = [
            item.strip()
            for item in questions
            if isinstance(item, str) and item.strip()
        ]
        if len(normalized_questions) != 3:
            raise ValueError("AI response must contain exactly three questions")

        return ProcessDraftResponse(
            extractedFields=normalized_fields,
            clarifyingQuestions=normalized_questions,
        )
    except Exception:
        logger.exception("AI draft processing failed; returning fallback")
        return _fallback()


@router.post("/process-draft", response_model=ProcessDraftResponse)
def process_draft(request: ProcessDraftRequest) -> ProcessDraftResponse:
    return processDraftWithAI(request.rawText, request.answers)
