from sqlmodel import Session, create_engine, select

# from config import Settings

db_url = "postgresql://postgres:091136@localhost:5432/CSCI3100"

engine = create_engine(db_url, echo=True)

def create_session():
    return Session(engine)
