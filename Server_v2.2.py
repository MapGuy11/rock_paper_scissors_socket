# Ben Shimmel, Connor Hackenberg
# CIT241
# Socket Program (Rock Paper Scissors)
# 04/27/2025

# Import all necessary libraries

import socket # Connection to the server
import json # For outputting the scores to a file. (JSON is my preferred format for this)
# Rich is for making cool text in the Console.
from rich import print

HOST = '0.0.0.0' # listen on all interfaces
PORT = 9888 # listen on port 9888
# Set Environment Variables some to send to the client. Some just for outputting scores.
GAME_READY = "GAME_START"
PLAY_AGAIN = "PLAY_AGAIN"
SCORES_FILE = 'scores.json'

# Load existing scores or initialize empty JSON file. Moving this file to a new server will keep the scores.
try:
    with open(SCORES_FILE, 'r') as f:
        scores = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    scores = {}

# Save scores
def save_scores():
    with open(SCORES_FILE, 'w') as f:
        json.dump(scores, f, indent=2)

# Determine winner username
def determine_winner(p1_move, p2_move, user1, user2):
    if p1_move == p2_move:
        return None  # tie
    wins = {('rock','scissors'), ('scissors','paper'), ('paper','rock')}
    if (p1_move, p2_move) in wins:
        return user1
    else:
        return user2

# Handle a full match: accept two, exchange usernames, play, update scores, ask replay
def play_match(server_sock):
    # Accept connections + List them on the console
    conn1, addr1 = server_sock.accept()
    print(f"Player1 connected from {addr1}")
    conn2, addr2 = server_sock.accept()
    print(f"Player2 connected from {addr2}")

    # Receive usernames (again not checking for duplicates or harmful usernames)
    user1 = conn1.recv(1024).decode().strip()
    user2 = conn2.recv(1024).decode().strip()
    print(f"Users: {user1} vs {user2}")

    # Ensure users in score dict
    for u in (user1, user2):
        scores.setdefault(u, 0)

    # send start
    conn1.send(GAME_READY.encode())
    conn2.send(GAME_READY.encode())

    # receive moves
    p1 = conn1.recv(1024).decode().lower()
    p2 = conn2.recv(1024).decode().lower()
    print(f"Moves: {p1}, {p2}")

    # determine winner and update
    winner = determine_winner(p1, p2, user1, user2)
    if winner:
        scores[winner] += 1
        save_scores()
        print(f"Winner: {winner}, updated scores: {scores}")
    else:
        print("It's a tie! No score change.")

    # send opponent moves to client to show on client side
    conn1.send(p2.encode())
    conn2.send(p1.encode())

    # ask play again if they get a yes from both players it will do a new game.
    conn1.send(PLAY_AGAIN.encode())
    conn2.send(PLAY_AGAIN.encode())
    w1 = conn1.recv(1024).decode().lower() == 'yes'
    w2 = conn2.recv(1024).decode().lower() == 'yes'
    print(f"Replay flags: {w1}, {w2}")

    # close both connections
    conn1.close()
    conn2.close()

    return w1 and w2

# Main loop
if __name__ == '__main__':
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f"Server listening on {HOST}:{PORT}")

# This helps with making sure the server is ready and waiting for players.
    try:
        while True:
            print("Waiting for a match...")
            replay = play_match(server)
            if replay:
                print("Both want replay — restarting match")
                continue
            print("At least one declined — waiting for next match")
    except KeyboardInterrupt:
        print("Shutting down server")
    finally:
        server.close()