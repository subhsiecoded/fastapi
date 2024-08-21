from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "postgresql://fastapi_c6q9_user:QaJUykwMkBaoGBCMSgJNacatqvYmlSWY@dpg-cr2ob12j1k6c73eau1r0-a.oregon-postgres.render.com/fastapi_c6q9"


engine= create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal= sessionmaker(autocommit = False, autoflush= False, bind= engine)

Base = declarative_base()

def get_db():
    db=SessionLocal()
    try: 
        return db
    except:
        db.close()

