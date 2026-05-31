import requests
import typer
from typing import Optional
from sqlmodel import Session, select, func
from database import engine, Media, Points, create_db_and_tables
from logic import *
from datetime import datetime, timedelta
from tablecreation import print_all_table, print_anime

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
    set_card_number = 10
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


def youtube_get_info(link: str,time_watched: int):
    pass

app = typer.Typer()
create_db_and_tables()

MEDIA_TYPES = ("youtube", "anime", "drama", "movie", "book", "physicalbook","vn", "manga")

@app.command()
def log(media_type: str, title: str, duration: float):

    if media_type not in MEDIA_TYPES:
        print("not a valid media type")
        print(MEDIA_TYPES)
    
    if media_type in ("movie", "anime"):
        
        season = int(input("enter season number: "))
        episode = int(input("enter episode number: "))

        media_type, title = map(str.lower,[media_type,title])
        media_data_inserter(media_type,title,duration,season,episode)
        points = time_based_scoring(duration)
        print(f"\nlogged {media_type} {title} Season {season} Episode {episode}\nfor a time of {duration}m\npoints earned: {points:.2f}\n")   
        
    elif media_type in ("book", "vn"):

        characters = int(input("enter character numbers read: "))
        media_data_inserter(media_type,title, duration,characters=characters)
        points = characters_read_based_scoring(characters)
        print(f"\nlogged {media_type} {title}\ncharacters read: {characters}\nfor a time of {duration}m\npoints earned: {points:.2f}\n")
       
@app.command()
def anki():
    anki_point_calculation()

@app.command()
def rma():
    remove_anki_points()
     

@app.command()
def points():
    points = get_points()
    print(f"total points: {points:.2f}")
    rank_up = 100
    print(f"points left until rank: {points:.2f}/{rank_up}")

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