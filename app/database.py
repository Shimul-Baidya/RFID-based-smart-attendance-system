from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import database_url

# The database URL needs to be correctly formatted for SQLAlchemy
# psycopg2 requires postgresql:// instead of postgres:// (which some PaaS providers use)
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

engine = create_engine(database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
