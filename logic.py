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




def scoring(duration: float,media_type: str):
    points_per_minute = 1/30
    unmodified_earned_points = points_per_minute * duration
    
    media_tags = {
        "youtube":"listening",
        "movie":"listening",
        "anime":"listening",
        "drama":"listening",
        "ln":"reading",
        "vn":"reading",
        "manga":"reading"
    }

    default_multipliers = {
        "listening":1,
        "reading":1,
        "anki":2
    }

    personalised_multipliers = {
        "listening":None,
        "reading":None,
        "anki":None
    }

    uranai_multipliers = {
        "listening":None,
        "reading": None,
        "anki": None
    }

    frozen_default_multiplier = MappingProxyType(default_multipliers)
    #frozen dict as these should not be changed

    for key in media_tags:
        if media_type == key:
            print(f"{key}:{media_tags[key]}")
            
            type = media_tags[key]
            #if type = media_tags[youtube] (type = listening)
            #therefore, default_multipliers[type] = 1
            

            #this bit will eventually take information from uranai multipliers, the option will also be whether to use regular or uranai multipliers
            user_input = input("would you like to use the default multiplier or try your luck with today's uranai. enter anything else for 'no' :").lower()
            
            if user_input == "uranai":
                base_multiplier = uranai_multipliers[type]
            
            else:
                base_multiplier = frozen_default_multiplier[type]
            
            if type != "listening":
            #checks if the string "type" is not listening (should be "reading")    
                    try:
                        characters_read = int(input("how many characters did you read? (if characters not tracked enter 0)\n"))
                    except ValueError:
                        print("you have inputted something invalid so it has been set to 0")
                        characters_read = 0
                    
                    if characters_read < 0:
                        print("can't be less than 0")
                        characters_read = 0
                
                    #takes the multiplier from the default_multipliers dictionary based off of the iterated category
                    characters_multiplier = 1+(characters_read/10000)
                    #formula for the read characters multiplier
                    reading_based_multiplier = characters_multiplier*base_multiplier

                    modified_points = unmodified_earned_points * reading_based_multiplier

                    print(f"the reading multiplier is {characters_multiplier:.3f}x and the base multiplier is {base_multiplier:.3f}x")
                    print(f"therefore the new multiplier is {reading_based_multiplier:.3f}x")
                    print(f"points earned: {modified_points:.2f}points")
                    #prints points as two decimal places as it makes output cleaner
                    return modified_points
            else:
                modified_points = unmodified_earned_points * base_multiplier
                print(f"the multiplier is {base_multiplier:.3f}x")
                print(f"points earned: {modified_points:.2f}points")
                return modified_points
                            
                    


def uranai_multipliers():
    pass

def uranai():
    pass


def log_update():
    pass

