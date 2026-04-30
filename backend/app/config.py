from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import Optional

class Settings(BaseSettings):
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "transport_db"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432

    @property
    def DB_URL(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    APP_NAME: str = "NetResilience app"
    DEBUG: bool = True

    MAX_NODES_FOR_FULL_CALCULATION: int = 500
    BETWEENNESS_SAMPLE_SIZE: Optional[int] = 300

    # Веса формулы интегрального коэффициента устойчивости:
    #   R = w_C·C + w_S·S + w_B·(1 − B)
    # Связность C — бинарный фундамент: разорванная сеть теряет ценность
    # независимо от остальных метрик, поэтому её вес наибольший.
    # Размер наибольшей компоненты S и инверсия концентрации нагрузки (1−B)
    # описывают независимые аспекты структурной устойчивости и оцениваются
    # равнозначно. Сумма коэффициентов = 1, R ∈ [0, 1].
    RESILIENCE_WEIGHT_CONNECTIVITY: float = 0.4
    RESILIENCE_WEIGHT_LARGEST_COMPONENT: float = 0.3
    RESILIENCE_WEIGHT_BETWEENNESS_INVERSE: float = 0.3

    # Скорости для оценки времени в маршруте A→B.
    # Средняя городская скорость с учётом светофоров, перекрёстков и средней
    # загрузки 40 км/ч — типичное значение для центральной части Москвы.
    # Скорость пешехода 5 км/ч — стандартная нормальная скорость взрослого.
    # Используются как простая аппроксимация: per-edge скорость потребовала бы
    # перегенерации графа с тегами maxspeed/highway из OSM.
    DEFAULT_DRIVING_SPEED_KMH: float = 40.0
    DEFAULT_WALKING_SPEED_KMH: float = 5.0

    ENABLE_CACHE: bool = True
    CACHE_HITS_THRESHOLD: int = 10

    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_TTL_GRAPH: int = 3600
    REDIS_TTL_ANALYSIS: int = 300
    REDIS_TTL_CASCADE: int = 300

    DISTRICTS_DATA_PATH: str = "app/data/districts"
    SAMPLE_GRAPHS_PATH: str = "app/data/sample_graphs"

    REQUEST_TIMEOUT_SECONDS: int = 30
    MAX_WORKERS: int = 4

    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173"
    ]

    SECRET_KEY: str = "your_secret_key_here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

settings = Settings()