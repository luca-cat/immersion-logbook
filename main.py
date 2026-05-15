import typer
from typing import Optional
from database import insert_into_table, log_deletion, total_points
from tablecreation import print_table

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

        insert_into_table(media_type, title, duration, details, link, notes)
        
        print(f"logged {media_type} {title} {detail_str} for a time of {duration}m")

        if link_str and notes_str:
            print(f"additional notes: {notes_str}")
            print(f"URL: {link_str}")
        elif link_str:
            print(f"additional notes: {link_str}")
        elif notes_str:
            print(f"URL: {notes_str}")
        
        points = total_points()
        print(f"total points: {points:.1f}")

@app.command()
def points():
    points = total_points()
    print(f"total points: {points:.1f}")

@app.command()
def setup():
    pass

@app.command()
def table():
    print_table()

@app.command()
def dl():
    log_deletion()

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