from sqlalchemy.orm import Session

from .models import Proposal, Profile, Task, Team
from .schemas import UNKNOWN_VALUE
from .task_rating import calculate_task_rating

DEMO_TEAMS = [
    ("Север", "Продуктовая команда", ["Анна", "Илья"], {"email": "north@example.test"}, ["образование", "сервисы"], ["исследование пользователей", "прототипирование"], ["React", "Python"]),
    ("Вектор", "Команда автоматизации", ["Мария", "Олег"], {"email": "vector@example.test"}, ["автоматизация", "малый бизнес"], ["API", "интеграции"], ["FastAPI", "Python"]),
    ("Пульс", "Команда клиентского опыта", ["Нина", "Роман"], {"email": "pulse@example.test"}, ["клиентский сервис"], ["UX", "тестирование"], ["React", "TypeScript"]),
    ("Маяк", "Команда аналитики", ["Елена", "Павел"], {"email": "mayak@example.test"}, ["аналитика", "данные"], ["визуализация", "анализ данных"], ["Python", "SQL"]),
    ("Контур", "Команда прототипирования", ["София", "Денис"], {"email": "contour@example.test"}, ["цифровые продукты"], ["дизайн интерфейсов", "разработка MVP"], ["React", "FastAPI"]),
]

DEMO_TASKS = [
    {
        "id": "demo-task-appointment",
        "title": "Автоматизация записи пациентов",
        "context_and_need": "Стоматологии нужен понятный процесс обработки обращений пациентов и записи на приём.",
        "data_and_materials": "Для демо используются сообщения пациентов без внешних интеграций.",
        "expected_result": "Рабочий прототип сценария записи пациентов через единый канал.",
        "success_criteria": "Команда показывает прототип и описывает проверяемый путь от сообщения до записи.",
        "limitations": "Демо не подключается к медицинской информационной системе.",
        "target_users": "Пациенты стоматологии и сотрудники, отвечающие за запись.",
        "business_contact": "Для демо контакт со стороны бизнеса не указан.",
        "interaction_format": "Еженедельная переписка и демонстрация прототипа.",
        "confirmed": True, "original_draft": "Демо-задача про запись пациентов.",
        "stage1_result": {"analyzed_draft": "Демо", "missing_aspects": [], "questions": []},
    },
    {
        "id": "demo-task-support",
        "title": "Навигация обращений клиентов",
        "context_and_need": "Команде поддержки нужен единый способ распределять обращения клиентов по темам.",
        "data_and_materials": "Для демо используются обезличенные примеры обращений из формы поддержки.",
        "expected_result": "Прототип очереди обращений с понятным приоритетом обработки.",
        "success_criteria": "Прототип позволяет найти обращение и показать его текущий статус.",
        "limitations": "Демо не подключается к реальным каналам поддержки.",
        "target_users": "Клиенты и сотрудники первой линии поддержки.",
        "business_contact": "Для демо контакт со стороны бизнеса не указан.",
        "interaction_format": "Асинхронные комментарии и короткая демонстрация.",
        "confirmed": True, "original_draft": "Демо-задача про поддержку.",
        "stage1_result": {"analyzed_draft": "Демо", "missing_aspects": [], "questions": []},
    },
    {
        "id": "demo-task-events",
        "title": "Планирование мероприятий сообщества",
        "context_and_need": "Небольшому сообществу сложно собирать заявки на локальные мероприятия в одном месте.",
        "data_and_materials": UNKNOWN_VALUE,
        "expected_result": "Команда подготовит понятный прототип страницы с перечнем мероприятий и заявками.",
        "success_criteria": UNKNOWN_VALUE,
        "limitations": UNKNOWN_VALUE,
        "target_users": UNKNOWN_VALUE,
        "business_contact": UNKNOWN_VALUE,
        "interaction_format": UNKNOWN_VALUE,
        "confirmed": True, "original_draft": "Демо-задача про мероприятия.",
        "stage1_result": {"analyzed_draft": "Демо", "missing_aspects": [], "questions": []},
    },
    {
        "id": "demo-task-inventory",
        "title": "Учёт остатков для мастерской",
        "context_and_need": "Мастерская вручную сверяет остатки расходных материалов и иногда обнаруживает нехватку поздно.",
        "data_and_materials": "Для демо есть обезличенная таблица материалов и пример приходных записей.",
        "expected_result": UNKNOWN_VALUE,
        "success_criteria": UNKNOWN_VALUE,
        "limitations": "Прототип работает только на демонстрационных данных без подключения к учётной системе.",
        "target_users": "Сотрудники мастерской, которые принимают материалы и следят за остатками.",
        "business_contact": UNKNOWN_VALUE,
        "interaction_format": UNKNOWN_VALUE,
        "confirmed": True, "original_draft": "Демо-задача про остатки материалов.",
        "stage1_result": {"analyzed_draft": "Демо", "missing_aspects": [], "questions": []},
    },
    {
        "id": "demo-task-feedback",
        "title": "Сбор отзывов после мероприятия",
        "context_and_need": "Организаторы получают обратную связь в разных каналах и хотят видеть ответы в одном месте.",
        "data_and_materials": "Доступны обезличенные примеры отзывов и тестовый список прошедших мероприятий.",
        "expected_result": "Нужен прототип формы обратной связи и страницы просмотра собранных ответов.",
        "success_criteria": "На демо можно отправить отзыв и увидеть его в общем списке без ручного переноса.",
        "limitations": "Доступ к реальным контактам участников и внешним сервисам для демо не предоставляется.",
        "target_users": UNKNOWN_VALUE,
        "business_contact": UNKNOWN_VALUE,
        "interaction_format": UNKNOWN_VALUE,
        "confirmed": True, "original_draft": "Демо-задача про отзывы.",
        "stage1_result": {"analyzed_draft": "Демо", "missing_aspects": [], "questions": []},
    },
]


def seed_demo_data(db: Session) -> None:
    teams = []
    for index, (name, description, members, contacts, interests, skills, technologies) in enumerate(DEMO_TEAMS, start=1):
        team_id = f"demo-team-{index}"
        team = db.get(Team, team_id)
        if not team:
            team = Team(id=team_id, name=name, description=description, members=members, contacts=contacts, interests=interests, skills=skills, technologies=technologies)
            db.add(team)
        else:
            if not team.interests:
                team.interests = interests
            if not team.skills:
                team.skills = skills
            if not team.technologies:
                team.technologies = technologies
        teams.append(team)
    for values in DEMO_TASKS:
        if not db.get(Task, values["id"]):
            db.add(Task(**values, **calculate_task_rating(values)))
    db.flush()
    if db.query(Proposal).filter(Proposal.id.like("demo-proposal-%")).count() == 0:
        for index, team in enumerate(teams, start=1):
            db.add(Proposal(
                id=f"demo-proposal-{index}", task_id="demo-task-appointment", team_id=team.id,
                idea=f"Идея команды {team.name} для сценария записи.",
                plan="Собрать прототип, проверить сценарий на демо-данных и показать результат.",
                deadline="2 недели", prototype_link="https://example.test/prototype", status="submitted",
            ))
    if db.query(Profile).filter(Profile.id.like("demo-business-%")).count() == 0:
        for index in range(1, 24):
            db.add(Profile(id=f"demo-business-{index}", role="business", name=f"Business Demo {index}", company=f"Example Studio {index}", description="Demo business profile for the platform presentation.", industry="Services and technology", city="Moscow", contacts={"email": f"business{index}@example.test"}))
    if db.query(Profile).filter(Profile.id.like("demo-freelancer-%")).count() == 0:
        for index in range(1, 36):
            db.add(Profile(id=f"demo-freelancer-{index}", role="freelancer", name=f"Freelancer Demo {index}", headline="AI Integration · Backend Python Developer", description="Demo freelancer profile for the platform presentation.", skills=["Python", "FastAPI", "React", "REST API", "LLM Integration"], experience="Demo experience: integrations and MVP prototypes.", city="Moscow", contacts={"email": f"freelancer{index}@example.test"}))
    db.commit()
