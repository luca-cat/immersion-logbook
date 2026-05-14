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
                if type == category:
                    multiplier = default_multipliers[category]
                    modified_points = unmodified_earned_points * multiplier
                    print(f"the multiplier is {multiplier}x")
                    print(f"points earned: {modified_points}")

                    

def uranai_multipliers():
    pass


def db_connection():
    load_dotenv()
    DB_PATH = os.getenv("DB_PATH")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    return conn, c


def create_table():
    conn, c = db_connection()
    #create table
    c.execute('''create table if not exists immersion
    (id integer primary key autoincrement, media_type text, title text, duration real, detail text, date text, link text, notes text)''')
    #commits changes//saves changes
    conn.commit()

def display_logs():
    conn, c = db_connection()
    c.execute('select * from immersion')
    
    for row in c.fetchall():
        print(row)

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
    conn, c = db_connection()
    create_table()
    conn.close()
    #close the cursor/closes the db connection

if __name__ == "__main__":
    main()

