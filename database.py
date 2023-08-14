import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

load_dotenv(".env")

engine = create_engine(os.environ['DATABASE_URL'], echo=True)
SESSION_LOCAL = sessionmaker(bind=engine)
Base = declarative_base()


def get_db():
    db = SESSION_LOCAL()
    try:
        yield db
    except:
        db.close()