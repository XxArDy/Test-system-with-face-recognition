import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    user = os.getenv("DB_USER", "root")
    password = os.getenv("DB_PASSWORD", "xxardy")
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", 3306)
    database = os.getenv("DB_NAME", "HPKTest")
    DATABASE_URL = f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}"

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)


SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)


class Base(declarative_base()):
    __abstract__ = True

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.__dict__}>"


def get_session() -> Session:
    """Return a new session with transaction management."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()
