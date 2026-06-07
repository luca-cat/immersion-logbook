import configparser
from rich.console import Console
from rich.table import Table
from sqlmodel import Session, select, func
from database import engine, Media, Points, create_db_and_tables

config = configparser.ConfigParser()
config.read('config.ini')


def table_customisation(starter_colour, fields):

    table = Table(title="immersion history", show_lines=True,width=100, expand=False)

    for field in fields:
        table.add_column(field, justify="left",style=starter_colour, overflow="fold")

    return table


def select_logs():

    with Session(engine) as session:
        statement = select(Media)
        results = session.exec(statement)
        logs = results.all()
        return logs

def print_anime():
    starter_colour = "#1104ff"
    fields = ('id','mediatype', 'title','season','episode', 'date')
    table = table_customisation(starter_colour, fields)
    with Session(engine) as session:
        statement = select(Media).where(Media.mediatype == "anime")
        results = session.exec(statement)
        logs = results.all()
    
    for row in logs:
        table.add_row(str(row.id),row.mediatype,row.title,str(row.season),str(row.episode),row.date)


    console = Console()
    console.print(table)

def print_all_table():
    
    colour = config['beginner']['colour']
    fields = ('id','mediatype','title','duration','season','episode','characters','date')

    table = table_customisation(colour, fields)

    for row in select_logs():
        
        table.add_row(str(row.id),
                        row.mediatype, 
                        row.title, 
                        str(row.duration) if row.duration else "",
                        str(row.season) if row.season else "", 
                        str(row.episode) if row.episode else"",
                        str(row.characters) if row.characters else "",
                        row.date) 

    console = Console()
    console.print(table)