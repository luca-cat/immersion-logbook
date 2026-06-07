import re
import requests
import typer
import subprocess
import configparser
from typing import Optional
from sqlmodel import Session, select, func
from database import engine, Media, Points, WatchList,create_db_and_tables
from logic import *
from datetime import datetime, timedelta
from tablecreation import print_all_table, print_anime

app = typer.Typer()
create_db_and_tables()

MEDIA_TYPES = ("youtube", "anime", "drama", "movie", "book", "physicalbook","vn", "manga")

config = configparser.ConfigParser()
config.read('config.ini')

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
    set_card_number = int(config['beginner']['new_cards'])
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

def watchlist_add(media_type: str, title:str):
    start_date = datetime.today().strftime('%Y-%m-%d')
    with Session(engine) as session:
        watchlist = WatchList(
            media_type=media_type,
            title=title,
            start_date=start_date
        )
        session.add(watchlist)
        session.commit()
        session.refresh(watchlist)

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


    time_based_points = time_based_scoring(duration)
    points_data_inserter("immersion", time_based_points, date, log_id=media_id)

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
        
        points_earned = time_based_scoring(duration)
        print(points_earned)
    else:
        print(f"{title}, {duration:.2f}")
        media_data_inserter(media_type,title,duration)

        points_earned = time_based_scoring(duration)
        print(points_earned)

@app.command()
def book(title: str, duration: float, start_page:int, end_page:int, total_pages_in_book:int):
    
    media_type = "physbook"

    #assumes the first page was read along with the last page being read fully
    total_pages_read = end_page - (start_page - 1)
    #an average of chars based off of lots of light novels
    average_total_chars_in_book = 130000

    chars_per_page = average_total_chars_in_book / total_pages_in_book

    chars_read = total_pages_read * chars_per_page
    chars_read = round(chars_read,0)
    
    print(f"read {title} for a duration of {duration}m")
    print(f"total pages read: {total_pages_read}")
    print(f"characters read this session: {chars_read}")

    media_data_inserter(media_type,title,duration,characters=chars_read)
    print(f"points earned: {time_based_scoring(duration)}")

@app.command()
def ln(title:str, duration:float, chars_read:int):
    
    media_type = "ln"

    print(f"read {title} for a duration of {duration}m")
    print(f"characters read this session: {chars_read}")

    media_data_inserter(media_type,title,duration,characters=chars_read)
    print(f"points earned: {time_based_scoring(duration)}")

@app.command()
def vn(title:str, duration:float, chars_read:int):
    
    media_type = "vn"

    print(f"read {title} for a duration of {duration}m")
    print(f"characters read this session: {chars_read}")

    media_data_inserter(media_type,title,duration,characters=chars_read)
    print(f"points earned: {time_based_scoring(duration)}")

@app.command()
def anime(title:str, duration:float, episode_identifier:str):
    
    media_type = "anime"

    episode_identifier = re.findall(r'\d+', episode_identifier)
    #finds the numbers from the episode identifier and sets episode_identifier to an array

    season = episode_identifier[0]
    episode = episode_identifier[1]
    print(f"watched {title} for a duration of {duration}m")
    print(f"Season: {season}")
    print(f"Episode: {episode}")

    media_data_inserter(media_type,title,duration,season,episode)
    points = time_based_scoring(duration)
    print(f"points earned: {points:.2f}\n")   

@app.command()
def movie(title:str, duration:float):
    
    media_type = "movie"

    print(f"watched {title} for a duration of {duration}m")

    media_data_inserter(media_type,title,duration,episode=1)
    points = time_based_scoring(duration)
    print(f"points earned: {points:.2f}\n")   

@app.command()
#adds to watchlist
def wla(media_type:str, title:str):
    watchlist_add(media_type,title)
    print(f"added {media_type} {title} to watchlist")


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

if __name__ == "__main__":
    app()