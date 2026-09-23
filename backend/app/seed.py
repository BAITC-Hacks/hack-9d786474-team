from sqlalchemy.orm import Session

from .models import Proposal, Task, Team

DEMO_TEAMS = [
    ("Север", "Продуктовая команда", ["Анна", "Илья"], {"email": "north@example.test"}),
    ("Вектор", "Команда автоматизации", ["Мария", "Олег"], {"email": "vector@example.test"}),
    ("Пульс", "Команда клиентского опыта", ["Нина", "Роман"], {"email": "pulse@example.test"}),
    ("Маяк", "Команда аналитики", ["Елена", "Павел"], {"email": "mayak@example.test"}),
    ("Контур", "Команда прототипирования", ["София", "Денис"], {"email": "contour@example.test"}),
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
        "status": "priority", "confirmed": True, "rating_total": 100,
        "rating_breakdown": {"context_and_need": 20, "data_and_materials": 20, "expected_result": 15, "success_criteria": 15, "limitations": 10, "target_users": 10, "business_contact_and_interaction_format": 10},
        "missing_fields": [], "original_draft": "Демо-задача про запись пациентов.",
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
        "status": "ready", "confirmed": True, "rating_total": 100,
        "rating_breakdown": {"context_and_need": 20, "data_and_materials": 20, "expected_result": 15, "success_criteria": 15, "limitations": 10, "target_users": 10, "business_contact_and_interaction_format": 10},
        "missing_fields": [], "original_draft": "Демо-задача про поддержку.",
        "stage1_result": {"analyzed_draft": "Демо", "missing_aspects": [], "questions": []},
    },
]


def seed_demo_data(db: Session) -> None:
    teams = []
    for index, (name, description, members, contacts) in enumerate(DEMO_TEAMS, start=1):
        team_id = f"demo-team-{index}"
        team = db.get(Team, team_id)
        if not team:
            team = Team(id=team_id, name=name, description=description, members=members, contacts=contacts)
            db.add(team)
        teams.append(team)
    for values in DEMO_TASKS:
        if not db.get(Task, values["id"]):
            db.add(Task(**values))
    db.flush()
    if db.query(Proposal).filter(Proposal.id.like("demo-proposal-%")).count() == 0:
        for index, team in enumerate(teams, start=1):
            db.add(Proposal(
                id=f"demo-proposal-{index}", task_id="demo-task-appointment", team_id=team.id,
                idea=f"Идея команды {team.name} для сценария записи.",
                plan="Собрать прототип, проверить сценарий на демо-данных и показать результат.",
                deadline="2 недели", prototype_link="https://example.test/prototype", status="submitted",
            ))
    db.commit()
