# NetResilience

Web-приложение для оценки устойчивости транспортной сети на основе графового анализа с ранжированием важных узлов.

---

## Что умеет приложение

- Отображает дорожную сеть семи смежных районов Москвы (1 298 узлов, 1 932 ребра) на интерактивной карте
- Вычисляет три метрики центральности (betweenness, closeness, degree) и ранжирует критические узлы
- Рассчитывает интегральный коэффициент устойчивости R ∈ [0, 1]
- Моделирует каскадные отказы с пошаговой деградацией устойчивости
- Строит кратчайший маршрут A → B по реальной топологии сети
- Показывает тепловую карту нагрузки по betweenness-центральности
- Экспортирует аналитический отчёт в PDF
- Сохраняет сценарии анализа и историю действий пользователя с поиском и фильтрацией
- Защищает эндпоинты rate-limiting'ом (slowapi + Redis) и JWT-аутентификацией

---

## Стек

| Слой | Технологии |
|------|-----------|
| Backend | Python 3.10, FastAPI, SQLAlchemy, Alembic, NetworkX, osmnx |
| Frontend | React 18, TypeScript, Zustand, React Leaflet, Tailwind CSS, Vite |
| Базы данных | PostgreSQL 15, Redis 7 |
| Мониторинг | Prometheus, Grafana |
| CI | GitHub Actions (pytest + ESLint + tsc build) |
| Инфраструктура | Docker, Docker Compose |

---

## Быстрый старт

### 1. Клонировать репозиторий

```bash
git clone https://github.com/willrain/NetResilience.git
cd NetResilience
```

### 2. Создать файлы окружения

**Корневой `.env`** — для Docker Compose (PostgreSQL, Grafana):

```bash
cp .env.docker.example .env
```

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=yourpassword
POSTGRES_DB=transport_db
POSTGRES_HOST=postgres

GRAFANA_ADMIN_PASSWORD=yourpassword
```

**`backend/.env`** — для FastAPI-приложения:

```bash
cp backend/.env.example backend/.env
```

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=yourpassword
POSTGRES_DB=transport_db
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

SECRET_KEY=замените_на_длинную_случайную_строку
REDIS_URL=redis://localhost:6379/0
ENABLE_CACHE=true
```

### 3. Запустить всё

```bash
docker compose up -d --build
```

Первый запуск собирает образы (~2–3 минуты). Последующие запуски — мгновенно.

| Сервис | URL |
|--------|-----|
| Приложение | http://localhost:3000 |
| API / Swagger | http://localhost:8000/docs |

---

### Режим разработки (без Docker для бэкенда и фронтенда)

Если нужен hot reload при разработке — запускай только инфраструктуру через Docker, а бэкенд и фронтенд вручную:

```bash
# Инфраструктура
docker compose up -d postgres redis

# Backend
cd backend
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
python run.py

# Frontend (в отдельном терминале)
cd frontend
npm install
npm run dev
```

Приложение в режиме разработки: [http://localhost:5173](http://localhost:5173).

---

## Мониторинг

| Сервис | URL | Логин |
|--------|-----|-------|
| Prometheus | http://localhost:9090 | — |
| Grafana | http://localhost:3001 | admin / `GRAFANA_ADMIN_PASSWORD` из `.env` |

Дашборд **NetResilience** подключается автоматически при первом запуске Grafana.  
Метрики бэкенда: RPS, latency p95, cache hit rate, ошибки 5xx.

---

## Тесты

```bash
cd backend
pytest --tb=short -q
```

391 тест: юнит-тесты алгоритмов и сервисов + интеграционные тесты маршрутов с реальными PostgreSQL и Redis через testcontainers. Каждый тест откатывает БД через транзакцию — данные не утекают между тестами.

---

## Структура проекта

```
NetResilience/
├── backend/
│   ├── app/
│   │   ├── routes/          # HTTP-маршруты (auth, graph, scenarios, history)
│   │   ├── services/        # Бизнес-логика и графовые вычисления
│   │   ├── repositories/    # Работа с БД
│   │   ├── schemas/         # Pydantic-модели
│   │   ├── models/          # SQLAlchemy-модели
│   │   └── data/districts/  # JSON-графы районов (генерируются скриптом)
│   ├── tests/               # pytest: юниты + интеграционные
│   ├── alembic/             # Миграции БД
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── pages/           # MapPage, ScenariosPage, HistoryPage, HelpPage
│   │   ├── components/      # Компоненты карты, панелей, UI
│   │   ├── store/           # Zustand-сторы
│   │   └── api/             # Axios-клиент с interceptors
│   └── package.json
├── grafana/                 # Provisioning datasource + dashboard
├── prometheus.yml
├── docker-compose.yml
├── .env.docker.example
└── backend/.env.example
```

---

## Данные

Граф загружается из OpenStreetMap через библиотеку `osmnx` и упрощается удалением промежуточных точек на прямых участках. Подготовка выполняется однократно скриптом в `scripts/`. Готовые JSON-файлы кладутся в `backend/app/data/districts/`.

Апробация: **7 смежных районов Москвы**, 1 298 узлов, 1 932 ребра, R = 0.8130, 260 критических узлов.
