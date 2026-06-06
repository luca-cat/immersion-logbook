import requests
import typer
import subprocess
from typing import Optional
from sqlmodel import Session, select, func
from database import engine, Media, Points, create_db_and_tables
from logic import *
from datetime import datetime, timedelta
from tablecreation import print_all_table, print_anime

app = typer.Typer()
create_db_and_tables()

MEDIA_TYPES = ("youtube", "anime", "drama", "movie", "book", "physicalbook","vn", "manga")

def show_valid_media_types():
    for x,y in enumerate(MEDIA_TYPES, start=1):
                print(f"{x}: {y}")


def get_points():
    with Session(engine) as session:
        statement = select(func.sum(Points.points))
        result = session.exec(statement).one()
        
        return result

def get_log_date():
    now = datetime.now()
    if 0 <= now.hour <=5:
    #anki resets everyday at 5am for this reason, any logs committed during the range of 12am and 5am are counted as the previous day
        return (now - timedelta(days=1)).strftime('%Y-%m-%d')
    #'now.hour' takes only the hour from now variable (0-23)
    #timedelta is simply expressing a unit of time. here it expresses one day.
    return now.strftime('%Y-%m-%d')

def today_finished_new_cards():

    payload = {
        
        "action":"findCards",
        "version":6,
        "params": {
            "query": "introduced:1"
            #introduced means new card completed
        }

    }
    try:
        r = requests.post('http://127.0.0.1:8765', json=payload)
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)
    #if any type of error is raised with the request, it stops the program and prints the error
    #'raise' stops the program deliberately

    anki_cards_dict = r.json()
    #takes the json request and creates a dictionary

    card_num = len(anki_cards_dict['result'])
    #counts number of new_cards completed today

    return card_num



def remove_anki_points():

    date_format_example = "YYYY-MM-DD"

    date = input(f"enter a date to input with the format {date_format_example}:\n")

    with Session(engine) as session:
        statement = select(Points).where(Points.tag == "anki").where(Points.date == date)
        results = session.exec(statement)
        
        try:
            points = results.one()
            #if date + anki tag are present it does not return None
            if points != None:
                print("Deleting anki points at date: ", date)
                session.delete(points)
                session.commit()
        except:
            print("row not found")


def anki_point_calculation():
    set_card_number = 30
    #set this for how many cards you want to complete per day

    points_per_card = 0.1

    total_points = set_card_number * points_per_card

    new_cards = today_finished_new_cards()

    date = get_log_date()

    with Session(engine) as session:
        statement = select(Points).where(Points.tag == "anki").where(Points.date == date)
        results = session.exec(statement)
        
        is_present = results.first()
        #checks if date is present, anki tagged and in points database. 
        
        if is_present != None:
            print("Points already earned today.\nCome back tomorrow ;)")
        
        elif is_present == None:
            
            if new_cards == set_card_number:
        
                print(f"Well done!\nuploading record to database on the date: {date}")
                points_data_inserter("anki", total_points, date, log_id=None)


            else:
                print(f"{new_cards}/{set_card_number} new cards completed. keep it up! ")
                print(f"if you complete your {set_card_number} cards you would get {total_points}points")


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

def media_data_inserter(media_type:str,title:str,duration:float, season: Optional[int] = None, episode: Optional[str] = None, characters: Optional[int] = None):

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
        reading_based_points = characters_read_based_scoring(characters)
        points_data_inserter("immersion", reading_based_points, date, log_id=media_id)

def youtube_get_information(link: str):
    result = subprocess.run(
        ["yt-dlp", "--print", "title", "--print", "duration", link],
        capture_output=True,
        text=True
    )
    lines = result.stdout.strip().split("\n")
    title = lines[0]
    duration = float(lines[1])/60
    return title, duration

@app.command()
def log(media_type: str, title: str, duration: float):
    
    media_type, title = map(str.lower,[media_type,title])
    
    try:   
        if media_type not in MEDIA_TYPES:
            print("not a valid media type")
            show_valid_media_types()
    
    except Exception as e:
        print(type(e).__name__, e)


    if media_type in ("movie", "anime", "drama"):
        
        season = int(input("enter season number: "))
        episode = int(input("enter episode number: "))

        media_data_inserter(media_type,title,duration,season,episode)
        points = time_based_scoring(duration)
        print(f"\nlogged {media_type} {title} Season {season} Episode {episode}\nfor a time of {duration}m\npoints earned: {points:.2f}\n")   
        
    elif media_type in ("book", "vn"):

        characters = int(input("enter character numbers read: "))
        if characters != 0:
            media_data_inserter(media_type,title, duration,characters=characters)
            points = characters_read_based_scoring(characters)
            print(f"\nlogged {media_type} {title}\ncharacters read: {characters}\nfor a time of {duration}m\npoints earned: {points:.2f}\n")
        else:
            media_data_inserter(media_type,title, duration)
            points = time_based_scoring(duration)
            print(f"\nlogged {media_type} {title}\ncharacters read: {characters}\nfor a time of {duration}m\npoints earned: {points:.2f}\n")

@app.command()
def mediatypes():
    show_valid_media_types()
#shows a list of valid loggable media types

@app.command()
def anki():
    anki_point_calculation()
#when prompted checks if daily anki quest has been completed

@app.command()
def rma():
    remove_anki_points()
#allows for removal of daily anki quest points    

@app.command()
def points():
    points = get_points()
    print(f"total points: {points:.2f}")
    rank_up = 100
    print(f"points left until rank: {points:.2f}/{rank_up}")

@app.command()
def yt(link: str):
    media_type = "youtube"
    title, duration = youtube_get_information(link)
    duration = round(duration, 2)
    #rounds the duration to two decimal places
    print(f"{title}, {duration:.2f}")
    custom_duration = float(input("would you like to enter a custom duration or assume the whole length of the video?\n"))
    
    if custom_duration > 0:
        duration = custom_duration
        print(f"{title}, {duration:.2f}")
        media_data_inserter(media_type,title,duration)
        time_based_scoring(duration)
    
    else:
        duration = duration
        print(f"{title}, {duration:.2f}")
        media_data_inserter(media_type,title,duration)
        time_based_scoring(duration)


@app.command()
def stats():
    print("total time immersed:\ntotal chars read:\nanime episodes watched\nmovies watched\ndramas episodes watched\nyoutube videos watched\n")

@app.command()
def setup():
    pass

@app.command()
def table():
    print_all_table()
    points()


@app.command()
def animetable():
    print_anime()
    points()

@app.command()
def dl():
    remove_log()

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

@app.command()
def rewards():
    pass

if __name__ == "__main__":
    app()