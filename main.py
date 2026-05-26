import typer
from typing import Optional
from sqlmodel import Session, select
from database import engine, Media, Points, create_db_and_tables
from datetime import datetime
from logic import characters_read_based_scoring, time_based_scoring


def remove_log():
    try: 
        id_choice = int(input("enter a log you'd like to remove: "))
        with Session(engine) as session:
            statement = select(Media).where(Media.id == id_choice)
            results = session.exec(statement)
            id_choice = results.one()
            
            print("deleting id: \n", id_choice)

            session.delete(id_choice)
            session.commit()
        

    except Exception as e:
        print(type(e).__name__, e)


def points_data_inserter(tag: str, points: float, date: str, log_id: int | None = None):
    
    with Session(engine) as session:
            point = Points(
                points=points,
                tag=tag,
                log_id=log_id,
                date=date
            )
            session.add(point)
            session.commit()

def media_data_inserter(media_type:str,title:str,duration:Optional[float] = None, season: Optional[int] = None, episode: Optional[str] = None, characters: Optional[int] = None):

    date = datetime.today().strftime('%Y-%m-%d')
    
    with Session(engine) as session:
            media = Media(
                mediatype=media_type,
                title=title,
                season=season,
                episode=episode,
                characters=characters,
                duration=duration,
                date=date)
            session.add(media)
            session.commit()
            session.refresh(media)
            media_id = media.id

    
    if media_type not in ("book", "vn", "physicalbook"):

        time_based_points = time_based_scoring(duration)
        points_data_inserter("immersion", time_based_points, date, log_id=media_id)

    else:
        reading_based_points = characters_read_based_scoring(characters,duration)
        points_data_inserter("immersion", reading_based_points, date, log_id=media_id)



def youtube_get_info(link: str,time_watched: int):
    pass

app = typer.Typer()
create_db_and_tables()

MEDIA_TYPES = ("youtube", "anime", "drama", "movie", "book", "physicalbook","vn", "manga")

@app.command()
def log(media_type: str, title: str):

    if media_type not in MEDIA_TYPES:
        print("not a valid media type")
        print(MEDIA_TYPES)
    
    if media_type == "anime":
        
        episode = int(input("enter episode number: "))
        season = int(input("enter season number: "))
        duration = float(input("enter time watched: "))

        media_type, title = map(str.lower,[media_type,title])
        media_data_inserter(media_type,title,duration,episode,season)
        print(f"logged {media_type} {title} Season {season} Episode {episode} for a time of {duration}m")   
        
    elif media_type in ("book", "vn"):

        characters = int(input("enter character numbers read: "))
        duration = float(input("enter time read: "))
        media_data_inserter(media_type,title, duration,characters=characters)

       

@app.command()
def points():
    pass

@app.command()
def setup():
    pass

@app.command()
def table():
    pass

@app.command()
def dl():
    remove_log()

@app.command()
def update_log():
    pass


@app.command()
def timer():
    print("test")

@app.command()
def fortune():
    pass

@app.command()
def dailies():
    pass

@app.command()
def weeklies():
    pass

@app.command()
def monthlies():
    pass

if __name__ == "__main__":
    app()