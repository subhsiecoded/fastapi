from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "postgresql://postgres:root%40!5702@localhost/fastapi"

engine= create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal= sessionmaker(autocommit = False, autoflush= False, bind= engine)

Base = declarative_base()

def get_db():
    db=SessionLocal()
    try: 
        return db
    except:
        db.close()

