# Ben Shimmel, Connor Hackenberg
# CIT241
# Socket Program (Rock Paper Scissors)
# 04/27/2025

# Import all necessary libraries
import socket # For Server Connection
# Rich is for making cool text in the Console. (also used in the server)
from rich.style import Style
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich import print


# Sets the console to use rich printing.
console = Console()
# Variables to store the host and port values (These are changed based on the menu choice)
HOST = None
PORT = None
# Flags sent from the server to the client to tell the client what to do.
GAME_READY = "GAME_START"
PLAY_AGAIN = "PLAY_AGAIN"

# Display a easy to use main menu.
def display_menu():
    # sub-title for the menu
    menu_text = Text("Select your server type:", style="bold magenta")
    menu_text.append("\n\n")
    menu_text.append("1. Connect to our server. (Auto)\n")
    menu_text.append("2. Connect to your own server. (Setup Required)\n")
    # exiting from here will NOT exit the server.
    menu_text.append("3. Exit Client")
    # Main title for the menu
    menu_panel = Panel(menu_text, title="[bold blue]Rock Paper Scissors Game | Menu [/bold blue]", expand=False)
    console.print(menu_panel)

# Handle on how we are connecting.
def choose_connection():
    global HOST, PORT
    while True:
        display_menu()
        choice = console.input("[bold yellow]Enter choice (1-3): [/bold yellow]")
            # User connects to our server.
        if choice == '1':
            HOST = 'home.connorhackenberg.tech'; PORT = 9888
            break
        # Handle when the user gives us their server.
        elif choice == '2':
            HOST = console.input("[bold cyan]Enter server host:[/bold cyan] ")
            PORT = int(console.input("[bold cyan]Enter server port:[/bold cyan] "))
            break
            # As stated above, exiting from here will NOT exit the server.
        elif choice == '3':
            console.print("[bold red]Exiting... Goodbye![/bold red]")
            raise SystemExit
        # Handle invalid input
        else:
            console.print("[red]Invalid selection, please choose 1, 2, or 3.[/red]")

# It helps us determine the winner of the game on both the client and server side.
def determine_winner(p1, p2):
    if p1 == p2:
        return "It's a tie!"
    wins = {('rock','scissors'), ('scissors','paper'), ('paper','rock')}
    if (p1,p2) in wins:
        return "[bold green]You Won! :crown:[/bold green]"
    return "[bold red]You Lost. :sob:[/bold red]"

# Play one round; return replay flag
def play_round(username):
    with socket.socket() as sock:
        sock.connect((HOST, PORT))
        # send username
        sock.send(username.encode())
        # wait start signal
        sig = sock.recv(1024).decode()
        if sig != GAME_READY:
            console.print(f"[red]Unexpected signal: {sig}[/red]")
            return False
        console.print("[bold green]Game is starting![/bold green]")

        # get move
        move = console.input("[bold magenta]Enter move ([green]rock[/green]/[yellow]paper[/yellow]/[cyan]scissors[/cyan]): [/bold magenta]").lower()
        while move not in ['rock','paper','scissors']:
            console.print("[red]Invalid move.[/red]")
            move = console.input("Enter rock, paper, or scissors: ").lower()
        sock.send(move.encode())

        # receive opponent move
        opp = sock.recv(1024).decode()
        console.print(f"[blue]You:[/blue] {move}  [blue]Opponent:[/blue] {opp}")
        console.print(determine_winner(move, opp))

        # ask replay
        sig2 = sock.recv(1024).decode()
        if sig2 != PLAY_AGAIN:
            return False
        resp = console.input("[bold yellow]Play again? ([green]yes[/green]/[red]no[/red]): [/bold yellow]").lower()
        sock.send(resp.encode())
        return resp == 'yes' or resp == 'y'


# Main function to run the game and to handle playing again.
if __name__ == '__main__':
    choose_connection()
    username = console.input("[bold cyan]Enter your username:[/bold cyan] ").strip()
    console.print(f"[green]Welcome, {username}![/green]")
    while True:
        retry = play_round(username)
        if not retry:
            console.print("[bold red]Thanks for playing. Goodbye![/bold red]")
            break
        console.print("[bold blue]Reconnecting for rematch...[/bold blue]")
