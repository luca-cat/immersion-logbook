from datetime import datetime
from types import MappingProxyType
import requests
from datetime import datetime, timedelta

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

    return card_num

def anki_point_calculation():
    set_card_number = 20
    #set this for how many cards you want to complete per day

    points_per_card = 0.1

    total_points = set_card_number * points_per_card

    new_cards = today_finished_new_cards()
    
    date = get_log_date()

    if new_cards == set_card_number:
        print(f"uploading record to database on the date: {date}")

    else:
        print(f"{new_cards}/20 completed. keep it up! ")
        print(f"if you complete your {set_card_number} cards you would get {total_points}points and also get points based off of time spent on your anki! ")




def characters_read_based_scoring(characters: int):

    character_constant = 10000
    #this constant is based on one's set difficulty 

    points_per_character_multiplier = 1/character_constant
        
    total_points = float(characters * points_per_character_multiplier)

    return total_points

def time_based_scoring(duration: int):
    points_per_minute = 1/60                     

    total_points = float(duration * points_per_minute)             

    return total_points

def uranai_multipliers():
    pass

def uranai():
    pass



def log_update():
    pass

