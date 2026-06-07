import os
from dotenv import load_dotenv
from typing import Annotated
from typing import Optional
from fastapi import Depends, FastAPI, HTTPException
from sqlmodel import Field, Session, SQLModel, create_engine, select, Relationship
from contextlib import asynccontextmanager
from sqlalchemy import event

class Media(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    mediatype: str = Field(index=True)
    title: str = Field(index=True)
    duration: float = Field(index=True)
    season: Optional[int] = None
    episode: Optional[int] = None
    characters: Optional[int] = None
    date: str = Field(index=True)
    #index=True creates an SQL index for column, allows for fast lookups
    points: list["Points"] = Relationship(back_populates="media", cascade_delete=True)

class Points(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    points: float = Field(default=None, index=True)
    tag: str = Field(index=True)
    log_id: int | None = Field(default=None, foreign_key="media.id", ondelete="CASCADE")
    date: str = Field(index=True)

    media: Optional[Media] = Relationship(back_populates="points")

class WatchList(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    media_type: str = Field(index=True)
    title: str = Field(index=True)
    start_date: str = Field(index=True)


load_dotenv()
sqlite_file_name = os.getenv("DB_PATH")
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
#allows fastapi to use sqlite in different threads
engine = create_engine(sqlite_url, connect_args=connect_args)

@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)


@app.post("/logs/")
def create_log(log: Media, session: SessionDep) -> Media:
    session.add(log)
    session.commit()
    session.refresh(log)
    return log

@app.get("/logs/")
def get_logs(session: SessionDep) -> list[Media]:
    logs = session.exec(select(Media)).all()
    return logs

@app.post("/points/")
def insert_points(point: Points, session: SessionDep) -> Points:
    session.add(point)
    session.commit()
    session.refresh(point)
    return point

@app.get("/points/")
def get_points(session: SessionDep) -> list[Points]:
    points = session.exec(select(Points)).all()
    return points

@app.post("/watchlistentries/")
def insert_new_entry(entry: WatchList, session: SessionDep) -> WatchList:
    session.add(entry)
    session.commit()
    session.refresh(entry)
    return entry

@app.get("watchlistentries/")
def get_entries(session: SessionDep) -> list[WatchList]:
    entries = session.exec(select(WatchList)).all()
    return entries

@app.delete("/logs/{id}")
def delete_log(id: int, session: SessionDep):
    id = session.get(Media, id)
    if not id:
        raise HTTPException(status_code=404, detail="log not found")
    session.delete(id)
    session.commit()
    return {"ok":True}