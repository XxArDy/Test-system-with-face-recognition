import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base

class Database:
    def __init__(self):
        self.DATABASE_URL = os.getenv("DATABASE_URL")
        if not self.DATABASE_URL:
            user = os.getenv("DB_USER", "xxardy")
            password = os.getenv("DB_PASSWORD", "xxardy")
            host = os.getenv("DB_HOST", "localhost")
            port = os.getenv("DB_PORT", 5432)
            database = os.getenv("DB_NAME", "HPKTest")
            self.DATABASE_URL = f"postgresql://{user}:{password}@{host}:{port}/{database}"

        self.engine = create_engine(
            self.DATABASE_URL
        )

        self.SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )

        self.Base = declarative_base()
    
    def get_base(self):
        return self.Base;
    
    def init_db(self):
        self.Base.metadata.create_all(self.engine)

    def get_session(self) -> Session:
        """Return a new session with transaction management."""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()


database = Database()