from openai import OpenAI
import json

client = OpenAI(
base_url="http://localhost:1234/v1",
api_key="lm-studio"
)

CANDIDATE = {
"name": "Yernar Ibadulla",
"position": "Middle AI Integration & Backend Python Developer",
"preferred_roles": [
"AI Integration Developer",
"AI Developer",
"AI Automation Developer",
"Backend Python Developer",
"Python Developer",
"Backend Developer",
"Integration Developer",
"Automation Developer",
"FullStack Developer",
"ETL Developer",
"BI Developer"
],
"skills": [
"Python",
"JavaScript",
"TypeScript",
"HTML5",
"CSS3",
"FastAPI",
"Node.js",
"REST API",
"Webhooks",
"Pydantic",
"HTTPX",
"Playwright",
"ngrok",
"LLM Integration",
"LLM",
"Local LLM",
"LM Studio",
"Function Calling",
"Prompt Engineering",
"Knowledge Base Design",
"AI Assistants",
"n8n",
"Make",
"NextBot",
"Workflow Automation",
"Browser Automation",
"amoCRM API",
"Google Calendar API",
"Google Sheets API",
"Kaspi API",
"Robokassa API",
"GViz API",
"PostgreSQL",
"SQLite",
"SQL",
"JSON",
"Git",
"GitHub",
"Linux",
"GitHub Pages",
"ITSM",
"Service Desk",
"SLA",
"CSAT",
"Release Management",
"Process Automation",
"Power BI"
],
"commercial_experience": [
"KCOI — IT Specialist, ITSM & Process Automation",
"S-Dental — AI Integration & Automation Developer",
"Кофейня «Штиль» — Full-Stack / Automation Developer"
],
"languages": {
"Russian": "Fluent",
"Kazakh": "Native",
"English": "B2 (IELTS Academic 6.5)"
}
}

SYSTEM_PROMPT = """
Ты — AI-рекрутер для оценки вакансий.

Твоя задача — определить, насколько вакансия подходит кандидату.

Кандидат позиционируется как:
Middle AI Integration & Backend Python Developer.

Главные направления кандидата:

* AI Integration
* AI Development
* AI Automation
* Backend Python
* Python
* API / Integrations
* Backend
* Workflow Automation
* LLM Integration
* FullStack с сильной backend/API составляющей
* ETL
* BI

Главное правило:

Оценивай НЕ количество совпавших технологий,
а основную работу, которую кандидат будет выполнять.

Не отклоняй вакансию только из-за отсутствия отдельной технологии,
если у кандидата есть разумная transferable foundation.

Например:

Python + REST API + backend
может быть хорошей основой для FastAPI/Django/Flask.

Python + API
может быть хорошей основой для HTTPX/Requests.

LLM + Function Calling + API integrations
может быть хорошей основой для LangChain/LangGraph.

SQL
может быть хорошей основой для PostgreSQL/MySQL.

НЕ считай автоматически hard blocker:

* Docker
* PostgreSQL
* Redis
* AWS
* Azure
* GCP
* pytest
* unittest
* Postman
* Requests
* HTTPX
* CI/CD
* LangChain
* LangGraph
* RAG

Hard blocker устанавливается ТОЛЬКО если:

1. отсутствующий навык является центральной специализацией вакансии;
2. без него кандидат фактически не сможет выполнять основную работу;
3. у кандидата нет разумной transferable foundation.

Примеры настоящего hard blocker:

* iOS Developer с обязательным Swift/iOS;
* Embedded C/C++ Engineer;
* ML Research Engineer;
* Computer Vision Research Engineer;
* другая принципиально отдельная специализация.

Senior / Lead / Principal вакансии обычно отклоняй.

Middle вакансии оценивай строго по обязанностям и требованиям.

Junior+ вакансии оценивай гибко.

Если вакансия требует 3-5+ лет обязательного commercial production experience,
а такого опыта у кандидата нет, это серьёзный негативный фактор.

Remote-вакансии для Python / AI / Backend / Automation / API / Integration
можно оценивать более гибко к вторичным технологиям.

S-Dental является подтверждённым commercial experience.

KCOI является подтверждённым commercial experience.

Не придумывай работодателей, годы опыта, технологии или обязанности.

Собственные проекты являются project experience, а не commercial experience.

Верни ТОЛЬКО JSON.

Формат:

{
"score": 0,
"should_apply": false,
"job_level": "unknown",
"direction_match": false,
"hard_blocker": false,
"hard_blocker_reason": "",
"commercial_experience_required": false,
"commercial_experience_mandatory": false,
"matched_skills": [],
"transferable_skills": [],
"missing_skills": [],
"critical_missing_skills": [],
"reason": "",
"cover_letter": ""
}

Оценка:

role_fit: 0-25
core_skill_fit: 0-30
task_fit: 0-20
experience_fit: 0-15
additional_fit: 0-10

Итоговый score = сумма всех пяти показателей.

Обычная вакансия:

score >= 75
+
direction_match = true
+
hard_blocker = false
+
нет обязательного Senior/Lead/Principal production experience

=> should_apply = true

Remote:

score >= 60
+
direction_match = true
+
hard_blocker = false
+
нет обязательного Senior/Lead/Principal production experience

=> should_apply = true

Если should_apply = false,
cover_letter должен быть пустым.

Если should_apply = true,
создай короткое естественное сопроводительное письмо примерно 400-700 символов.

Язык письма определяй по DESCRIPTION вакансии,
а НЕ по названию должности.

Если description преимущественно русский — русский.

Если преимущественно казахский — казахский.

Если преимущественно английский — английский.

Название должности и слово Remote язык не определяют.

Используй только подтверждённые навыки и опыт.

Не выдавай transferable skill за подтверждённый коммерческий опыт.

Каждое сопроводительное письмо ОБЯЗАНО заканчиваться ТОЧНО:

Я готов к живому интервью и готов доказать свои способности!

После этой фразы не должно быть никакого текста.
"""

vacancy = """
Название:
Python Junior Developer

Описание:
Мы ищем Python Junior Developer в команду разработки.

Обязанности:

* разработка backend-сервисов на Python;
* работа с REST API;
* интеграция внешних сервисов;
* написание небольших автоматизационных скриптов;
* работа с базами данных;
* исправление ошибок и развитие существующих сервисов.

Требования:

* Python;
* базовое понимание REST API;
* SQL;
* Git;
* желание развиваться в backend-разработке;
* опыт с FastAPI будет преимуществом.
  """

user_prompt = f"""
ПРОФИЛЬ КАНДИДАТА:

{json.dumps(CANDIDATE, ensure_ascii=False, indent=2)}

ВАКАНСИЯ:

{vacancy}

Проанализируй вакансию согласно правилам system prompt.

Верни только JSON.
"""

response = client.chat.completions.create(
model="qwen/qwen3-vl-8b",
messages=[
{
"role": "system",
"content": SYSTEM_PROMPT
},
{
"role": "user",
"content": user_prompt
}
],
temperature=0.1,
max_tokens=1500,
)

result = response.choices[0].message.content

print(result)
