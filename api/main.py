from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, timedelta
from enum import Enum
import uuid

app = FastAPI(
    title="HR-портал «РусГидро» API",
    description="Backend API для системы мотивации персонала",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()

# ============ ENUMS ============
class ModuleCategory(str, Enum):
    RECOGNITION = "recognition"
    CAREER = "career"
    SAFETY = "safety"
    WELLNESS = "wellness"
    ECO = "eco"
    INNOVATION = "innovation"

class ChallengeStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    PENDING = "pending"

# ============ MODELS ============
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    full_name: str
    department: str
    position: str
    email: str
    avatar_url: Optional[str] = None
    points: int = 0
    badges: List[str] = []
    career_level: str = "Стажер"
    years_of_service: int = 0
    created_at: datetime = Field(default_factory=datetime.now)

class GratitudeCreate(BaseModel):
    recipient_id: str
    category: str
    message: str
    points: int = Field(default=50, ge=10, le=500)

class Gratitude(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    sender_id: str
    sender_name: str
    recipient_id: str
    recipient_name: str
    category: str
    message: str
    points: int
    created_at: datetime = Field(default_factory=datetime.now)
    likes: int = 0

class Challenge(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    category: ModuleCategory
    points_reward: int
    status: ChallengeStatus = ChallengeStatus.ACTIVE
    deadline: Optional[datetime] = None
    participants_count: int = 0
    completed_count: int = 0

class LeaderboardEntry(BaseModel):
    rank: int
    user_id: str
    full_name: str
    department: str
    points: int
    badges_count: int

class ProjectStage(BaseModel):
    id: int
    title: str
    description: str
    start_month: int
    end_month: int
    status: str
    deliverables: List[str]

class BudgetItem(BaseModel):
    category: str
    q1: float
    q2: float
    q3: float
    q4: float
    total: float

# ============ MOCK DATA ============
users_db = [
    User(id="u1", full_name="Мария Соколова", department="Оператор ГЭС", position="Старший оператор", email="m.sokolova@rusgidro.ru", points=4820, badges=["Безопасность", "Наставник", "Эко-активист"], career_level="Ведущий специалист", years_of_service=5),
    User(id="u2", full_name="Дмитрий Волков", department="ИТ-отдел", position="Ведущий разработчик", email="d.volkov@rusgidro.ru", points=4150, badges=["Инноватор", "Эксперт"], career_level="Ведущий специалист", years_of_service=4),
    User(id="u3", full_name="Анна Петрова", department="Инженер-монтажник", position="Инженер", email="a.petrova@rusgidro.ru", points=3980, badges=["Быстрое реагирование", "Командность"], career_level="Специалист", years_of_service=3),
    User(id="u4", full_name="Иван Кузнецов", department="Энергетик", position="Энергетик", email="i.kuznetsov@rusgidro.ru", points=3200, badges=["Безопасность"], career_level="Специалист", years_of_service=2),
    User(id="u5", full_name="Алексей Козлов", department="Инженер-энергетик", position="Инженер", email="a.kozlov@rusgidro.ru", points=2450, badges=["Новичок"], career_level="Специалист", years_of_service=1),
]

gratitudes_db = [
    Gratitude(id="g1", sender_id="u5", sender_name="Алексей Козлов", recipient_id="u3", recipient_name="Анна Петрова", category="Быстрое реагирование", message="Анна оперативно выявила неполадку в трансформаторе и предотвратила простой станции. Благодарю за профессионализм!", points=50, likes=12),
    Gratitude(id="g2", sender_id="u1", sender_name="Мария Соколова", recipient_id="u2", recipient_name="Дмитрий Волков", category="Инновация", message="Дмитрий разработал автоматизированную систему мониторинга, которая сократила время диагностики на 40%. Отличная работа!", points=100, likes=24),
]

challenges_db = [
    Challenge(id="c1", title="Найди опасность", description="Сфотографируй риск на рабочем месте и получи баллы", category=ModuleCategory.SAFETY, points_reward=30, deadline=datetime.now() + timedelta(days=7)),
    Challenge(id="c2", title="Квиз: Регламенты ТО", description="10 вопросов на знание регламентов технического обслуживания", category=ModuleCategory.SAFETY, points_reward=50, deadline=datetime.now() + timedelta(days=14)),
    Challenge(id="c3", title="Эко-челлендж: раздельный сбор", description="Загрузи фото раздельного сбора мусора на рабочем месте", category=ModuleCategory.ECO, points_reward=40, deadline=datetime.now() + timedelta(days=5)),
    Challenge(id="c4", title="Приведи коллегу", description="Рекомендуй специалиста на дефицитную позицию", category=ModuleCategory.CAREER, points_reward=2000, deadline=datetime.now() + timedelta(days=30)),
]

project_stages = [
    ProjectStage(id=1, title="Аналитика и проектирование", description="Исследование, ТЗ, прототипы, согласование бюджета", start_month=1, end_month=2, status="Завершено", deliverables=["Техническое задание", "Прототипы UI", "Согласованный бюджет"]),
    ProjectStage(id=2, title="MVP и тестирование", description="Разработка ядра, пилот на 500 пользователях", start_month=3, end_month=4, status="В работе", deliverables=["MVP платформы", "Отчет пилота", "Баг-лист"]),
    ProjectStage(id=3, title="Расширение функционала", description="Интеграция всех 17 модулей, обучение HR", start_month=5, end_month=6, status="Запланировано", deliverables=["17 модулей", "Обученные HR-менеджеры", "Документация"]),
    ProjectStage(id=4, title="Полномасштабный запуск", description="Ролл-аут на все филиалы, маркетинговая кампания", start_month=7, end_month=9, status="Запланировано", deliverables=["30 000+ пользователей", "Маркетинговые материалы", "PR-кампания"]),
    ProjectStage(id=5, title="Оптимизация и масштабирование", description="Аналитика, доработки, подготовка годового отчета", start_month=10, end_month=12, status="Запланировано", deliverables=["Годовой отчет", "Оптимизированная платформа", "План на следующий год"]),
]

budget_items = [
    BudgetItem(category="Проектирование и аналитика", q1=1.2, q2=0, q3=0, q4=0, total=1.2),
    BudgetItem(category="Разработка ПО", q1=2.5, q2=5.8, q3=4.2, q4=1.0, total=13.5),
    BudgetItem(category="Интеграции (SAP, 1C, AD)", q1=0, q2=1.5, q3=1.0, q4=0.5, total=3.0),
    BudgetItem(category="Фонд мотивации", q1=0, q2=0.5, q3=3.5, q4=4.2, total=8.2),
    BudgetItem(category="Маркетинг и коммуникации", q1=0.3, q2=0.2, q3=1.5, q4=0.5, total=2.5),
    BudgetItem(category="Инфраструктура", q1=0.2, q2=0.5, q3=1.0, q4=1.0, total=2.7),
    BudgetItem(category="Обучение и поддержка", q1=0, q2=0.3, q3=0.5, q4=0.3, total=1.1),
]

# ============ AUTH ============
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    # В реальном проекте — валидация JWT токена
    return users_db[4]  # Алексей Козлов

# ============ ENDPOINTS ============
@app.get("/")
async def root():
    return {
        "name": "HR-портал «РусГидро» API",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs"
    }

@app.get("/api/users/me", response_model=User)
async def get_current_user_profile(user: User = Depends(get_current_user)):
    return user

@app.get("/api/users/leaderboard", response_model=List[LeaderboardEntry])
async def get_leaderboard(limit: int = 10):
    sorted_users = sorted(users_db, key=lambda x: x.points, reverse=True)
    return [
        LeaderboardEntry(
            rank=idx + 1,
            user_id=u.id,
            full_name=u.full_name,
            department=u.department,
            points=u.points,
            badges_count=len(u.badges)
        )
        for idx, u in enumerate(sorted_users[:limit])
    ]

@app.get("/api/users/{user_id}", response_model=User)
async def get_user(user_id: str):
    user = next((u for u in users_db if u.id == user_id), None)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user

@app.post("/api/gratitude", response_model=Gratitude)
async def create_gratitude(gratitude: GratitudeCreate, user: User = Depends(get_current_user)):
    recipient = next((u for u in users_db if u.id == gratitude.recipient_id), None)
    if not recipient:
        raise HTTPException(status_code=404, detail="Получатель не найден")

    new_gratitude = Gratitude(
        sender_id=user.id,
        sender_name=user.full_name,
        recipient_id=recipient.id,
        recipient_name=recipient.full_name,
        category=gratitude.category,
        message=gratitude.message,
        points=gratitude.points
    )
    gratitudes_db.insert(0, new_gratitude)

    # Начисляем баллы получателю
    recipient.points += gratitude.points

    return new_gratitude

@app.get("/api/gratitude", response_model=List[Gratitude])
async def get_gratitudes(limit: int = 20, offset: int = 0):
    return gratitudes_db[offset:offset + limit]

@app.get("/api/challenges", response_model=List[Challenge])
async def get_challenges(category: Optional[ModuleCategory] = None):
    if category:
        return [c for c in challenges_db if c.category == category]
    return challenges_db

@app.post("/api/challenges/{challenge_id}/complete")
async def complete_challenge(challenge_id: str, user: User = Depends(get_current_user)):
    challenge = next((c for c in challenges_db if c.id == challenge_id), None)
    if not challenge:
        raise HTTPException(status_code=404, detail="Челлендж не найден")

    user.points += challenge.points_reward
    challenge.completed_count += 1

    return {
        "message": f"Челлендж '{challenge.title}' пройден!",
        "points_earned": challenge.points_reward,
        "total_points": user.points
    }

@app.get("/api/project/stages", response_model=List[ProjectStage])
async def get_project_stages():
    return project_stages

@app.get("/api/project/budget", response_model=List[BudgetItem])
async def get_budget():
    return budget_items

@app.get("/api/project/metrics")
async def get_metrics():
    return {
        "engagement_target": 85,
        "engagement_current": 62,
        "turnover_reduction": 25,
        "safety_improvement": 40,
        "rationalization_proposals": 500,
        "estimated_savings_rub": 45000000,
        "roi_percent": 240,
        "eco_involvement": 80,
        "burnout_reduction": 30,
        "total_users": 30000,
        "active_users_today": 12450,
        "gratifications_sent_this_month": 3420,
        "challenges_completed_this_month": 8765
    }

@app.get("/api/modules")
async def get_modules():
    modules = [
        {"id": 1, "title": "Энергия благодарности", "category": "recognition", "description": "Публичные благодарности коллегам", "points_available": 150},
        {"id": 2, "title": "Карьерный навигатор", "category": "career", "description": "Персональные карьерные треки", "points_available": 0},
        {"id": 3, "title": "Марафон безопасности", "category": "safety", "description": "Челленджи на знание регламентов", "points_available": 200},
        {"id": 4, "title": "Рационализаторские предложения", "category": "innovation", "description": "Автоматический расчет экономического эффекта", "points_available": 5000},
        {"id": 5, "title": "Клуб наставников", "category": "career", "description": "Накопительная мотивация за адаптацию", "points_available": 500},
        {"id": 6, "title": "Семейные мероприятия", "category": "wellness", "description": "Экскурсии, конкурсы, старты", "points_available": 150},
        {"id": 7, "title": "Забота о себе", "category": "wellness", "description": "Анти-выгорание и wellness", "points_available": 300},
        {"id": 8, "title": "Герой смены", "category": "recognition", "description": "Еженедельное полевое голосование", "points_available": 200},
        {"id": 9, "title": "Кросс-дивизиональный обмен", "category": "innovation", "description": "Мастер-классы между филиалами", "points_available": 600},
        {"id": 10, "title": "Эко-челлендж", "category": "eco", "description": "Соревнования по экологическим практикам", "points_available": 200},
        {"id": 11, "title": "Долгосрочная лояльность", "category": "recognition", "description": "Градация поощрений по стажу", "points_available": 0},
        {"id": 12, "title": "Тренажер ценностей", "category": "recognition", "description": "Геймифицированные квесты", "points_available": 250},
        {"id": 13, "title": "Приведи коллегу", "category": "career", "description": "Реферальная программа", "points_available": 5000},
        {"id": 14, "title": "Инженерные конкурсы", "category": "innovation", "description": "Ежемесячные соревнования", "points_available": 500},
        {"id": 15, "title": "Персональный дашборд", "category": "recognition", "description": "Визуализация прогресса", "points_available": 0},
        {"id": 16, "title": "Мотивация в оптимизации", "category": "innovation", "description": "Приемы формирования мотивации", "points_available": 0},
        {"id": 17, "title": "Управление мотивацией", "category": "innovation", "description": "Система управления заинтересованностью", "points_available": 0},
    ]
    return modules

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
