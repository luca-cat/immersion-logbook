from dotenv import load_dotenv
import os
import sqlite3
from datetime import datetime

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

    for key in media_tags:
        if media_type == key:
            print(f"{key}:{media_tags[key]}")
            
            type = media_tags[key]

            for category in default_multipliers:
                if type != "listening":
                #checks if the string "type" is not listening (should be "reading")    
                    if category == type :
                        characters_read = int(input("how many characters did you read?\n"))
                        multiplier = default_multipliers[category]
                        #takes the multiplier from the default_multipliers dictionary based off of the iterated category
                        characters_multiplier = 1+(characters_read/10000)
                        #formula for the read characters multiplier
                        new_multiplier = characters_multiplier*multiplier

                        modified_points = unmodified_earned_points * new_multiplier

                        print(f"the reading multiplier is {characters_multiplier}x and the base multiplier is {multiplier}x")
                        print(f"therefore the new multiplier is {new_multiplier}x")
                        print(f"points earned: {modified_points:.2f}points")
                        #prints points as two decimal places as it makes output cleaner
                else:
                    if type == category:
                        multiplier = default_multipliers[category]
                        modified_points = unmodified_earned_points * multiplier
                        print(f"the multiplier is {multiplier}x")
                        print(f"points earned: {modified_points:.2f}points")
                            
                    

def uranai_multipliers():
    pass


def db_connection():
    load_dotenv()
    #reads the .env file
    DB_PATH = os.getenv("DB_PATH")
    #takes DB_PATH from .env and sets it to variable DB_PATH

    conn = sqlite3.connect(DB_PATH)
    #connects to the database
    c = conn.cursor()
    #creates an sql cursor which allows for reading and writing of DB
    return conn, c
    #returns so that when a database related function is called it allows for connection to DB and modifying of DB

def create_table():
    conn, c = db_connection()
    #create table
    c.execute('''create table if not exists immersion
    (id integer primary key autoincrement, media_type text, title text, duration real, detail text, date text, link text, notes text)''')
    #commits changes//saves changes
    conn.commit()

def log_deletion():
    conn, c = db_connection()

    chosen_id = int(input("enter the id you would like to remove"))
    print(f"deleting log: {chosen_id}")
    c.execute('delete from immersion where id = ?', (chosen_id,))
    #the variable from python has to be a tuple

    conn.commit()

def fetch_all():
    conn, c = db_connection()
    c.execute("select * from immersion")
    rows = c.fetchall()
    conn.close()
    return rows

def log_update():
    pass


def insert_into_table(media_type:str, title:str, duration:float, details:str, link:str,notes:str):
    conn, c = db_connection()
    date = datetime.today().strftime('%Y-%m-%d')
    c.execute('''insert into immersion (media_type, title, duration, detail, date, link, notes) values (?,?,?,?,?,?,?)''',(media_type,title,duration,details,date,link,notes))
    conn.commit()

def main():
    conn = db_connection()
    #prompts db_connection() to connect to the database
    create_table()
    conn.close()
    #close the cursor/closes the db connection
if __name__ == "__main__":
    main()

