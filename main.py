import typer
from typing import Optional
from sqlmodel import Session
from database import engine, Media
from datetime import datetime

def media_data_inserter(media_type:str,title:str,duration:float, notes: Optional[str] = None, details: Optional[str] = None, link: Optional[str] = None):
    with Session(engine) as session:
            media = Media(
                mediatype=media_type,
                title=title,
                duration=duration,
                date=datetime.today().strftime('%Y-%m-%d')
                notes=notes
                details=details
                link=link)
            session.add(media)
            session.commit()

def points_data_inserter():
    with Session(engine) as session:
            media = Points(
                mediatype=media_type,
                title=title,
                duration=duration,
                date=datetime.today().strftime('%Y-%m-%d')
                notes=notes
                details=details
                link=link)
            session.add(media)
            session.commit()


def youtube_get_info(link: str,time_watched: int):
    pass

app = typer.Typer()

MEDIA_TYPES = ("youtube", "anime", "drama", "movie", "ln", "vn", "manga")

@app.command()
def log(media_type: str, title: str, duration: float, notes: Optional[str] = None, details: Optional[str] = None, link: Optional[str] = None):
    
    if media_type not in MEDIA_TYPES:
        print("not a valid media type")
        print(MEDIA_TYPES)
    
    else: 
        detail_str = details if details else ""
        notes_str = notes if notes else ""
        link_str = link if link else ""
        #if notes contains a value then notes_str equal to string, else it equals none
        media_type, title = map(str.lower,[media_type,title])
        media_data_inserter(media_type,title,duration,detail_str,notes_str,link_str)
        
        print(f"logged {media_type} {title} {detail_str} for a time of {duration}m")

        if link_str and notes_str:
            print(f"additional notes: {notes_str}")
            print(f"URL: {link_str}")
        elif link_str:
            print(f"additional notes: {link_str}")
        elif notes_str:
            print(f"URL: {notes_str}")
        
        
       

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
    pass

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