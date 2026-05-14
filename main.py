import typer
from typing import Optional
from database import insert_into_table, display_logs, log_deletion
from tablecreation import print_table

app = typer.Typer()
#allows for -h to be used as a help alias

@app.command()
def log(media_type: str, title: str, duration: float, notes: Optional[str] = None, details: Optional[str] = None, link: Optional[str] = None):
    detail_str = f"{details} " if details else ""
    notes_str = f":{notes}" if notes else ""
    link_str = f"{link} if" if link else ""
    #if notes contains a value then notes_str equal to string, else it equals none
    insert_into_table(media_type, title, duration, details, link, notes)
    print(f"logged {media_type} {title} {detail_str}{duration}m{notes_str}. {link_str}")


@app.command()
def show_table():
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