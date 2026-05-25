from typing import Annotated
from typing import Optional
from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, create_engine, select
from contextlib import asynccontextmanager



class Media(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    mediatype: str = Field(index=True)
    title: str = Field(index=True)
    duration: float = Field(default=None, index=True)
    detail: Optional[str] = None
    date: str = Field(index=True)
    link: Optional[str] = None
    notes: Optional[str] = None
    #index=True creates an SQL index for column, allows for fast lookups


sqlite_file_name = 'testlogs.db'
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
#allows fastapi to use sqlite in different threads
engine = create_engine(sqlite_url, connect_args=connect_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

app = FastAPI()

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