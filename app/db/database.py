from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import create_engine


DATABASE_URL = "sqlite:///./BankingApp.db"  # simple SQLite for now

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}  # Only for SQLite
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
