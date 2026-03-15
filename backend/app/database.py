from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session, DeclarativeBase
from .config import settings

class Base(DeclarativeBase): 
    pass

engine = create_engine(
    settings.DB_URL,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    Base.metadata.create_all(bind=engine)

def check_connection() -> bool:
    try:
        with engine.connect() as conn:
            conn.execute(text("Select 1"))
        print("Connected to database successfully.")
        return True
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return False