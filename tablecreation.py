from rich.console import Console
from rich.table import Table
from database import fetch_all

def print_table():
    starter_colour = "#ff0404"
    ranks = {"beginner":"#ff0404",
            "intermediate":"pink",}
    #ranks work in progress

    table = Table(title="immersion history", show_lines=True)
    args = ('id','mediatype', 'title', 'duration', 'detail', 'date')

    for arg in args:
        table.add_column(arg, justify="left",style=starter_colour, overflow="fold")

    theme = {}

    for row in fetch_all():
        table.add_row(str(row[0]),str(row[1]), str(row[2]), f"{row[3]}m", "" if row[4] is None else str(row[4]), str(row[5]))

    console = Console()
    console.print(table)


