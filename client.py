# ----------------------- Imports -----------------------
import pygame as pg
from threading import *

from socket import *

import time

from player import Player

# ----------------------- Variables -----------------------

SERVER_IP = "10.188.222.194" #"localhost"
SERVER_PORT = 9998
CONNECTED = False
DISCONNECTION_WAIT = 5

FPS = 60

SIZE = None
SCREEN = None

USERNAME = "John"
PLAYERS = []

WAITING_TIME = 0.01 # in seconds
TIMEOUT = 10 # in seconds

PING = None # in milliseconds

# ----------------------- Threads -----------------------

def display():
    """Thread to display the current state of the game given by the server.
    """
    
    global SCREEN
    global PLAYERS
    
    clock = pg.time.Clock()
    
    while CONNECTED:
        
        SCREEN.fill((0, 0, 0))  # May need to be custom
        
        for player in PLAYERS:
            pg.draw.rect(SCREEN, player.color, [player.position, player.size])
        
        pg.display.update()
        
        clock.tick(FPS)



def game():
    """Thread to send inputs to the server, receive the current state of the game from it, and update the client-side variables.
    """
    
    global PLAYERS
    global SERVER_IP
    global SERVER_PORT
    
    while CONNECTED:
        
        inputs = getInputs()
        
        state = send(inputs)
        
        update(state)



# ----------------------- Functions -----------------------

def connect():
    """Try to connect to the given SERVER_IP and SERVER_PORT. When successful, initialize the current state of the game.

    Returns:
        bool: is the connection successful ?
    """
    
    global SIZE
        
    message = send("CONNECT " + USERNAME + " END")
    
    messages = message.split(" ")
    
    if messages[0] == "CONNECTED" and messages[1] == USERNAME and messages[3] == "STATE":
        SIZE = eval(messages[2])
        if SIZE == None:
            SIZE = (400, 300)   # Some default size.
        
        beginIndex = len(messages[0]) + len(messages[1]) + len(messages[2]) + 3 # 3 characters 'space'
        update(message[beginIndex - 1:])
        
        return True

    return False



def getInputs():
    """Get inputs from the keyboard and generate the corresponding request to send to the server.

    Returns:
        str: the normalized request to send to the server : "INPUT <Username> <Input> END"
    """
    
    events = pg.event.get()
    
    for event in events:
        if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
            exit()
        elif event.type == pg.KEYDOWN:
            if event.key in [pg.K_LEFT, pg.K_q]:
                return "INPUT " + USERNAME + " L END"
            elif event.key in [pg.K_RIGHT, pg.K_d]:
                return "INPUT " + USERNAME + " R END"
            elif event.key in [pg.K_UP, pg.K_z]:
                return "INPUT " + USERNAME + " U END"
            elif event.key in [pg.K_DOWN, pg.K_s]:
                return "INPUT " + USERNAME + " D END"
    
    return "INPUT " + USERNAME + " . END"



def send(input="INPUT " + USERNAME + " . END"):
    """Send a normalized request to the server and listen for the normalized answer.

    Args:
        input (str): Normalized request to send to the server. Defaults to "INPUT <Username> . END".

    Returns:
        str: the normalized answer from the server.
    """
    
    global PING
    
    with socket(AF_INET, SOCK_STREAM) as sock:
        t = time.time()
        
        # send data
        sock.connect((SERVER_IP, SERVER_PORT))
        sock.sendall(bytes(input, "utf-16"))
        
        
        # receive answer
        answer = str(sock.recv(1024*2), "utf-16")
        
        PING = int((time.time() - t) * 1000)
        print("Ping (ms) = ", PING)
        
        return answer



def update(state="STATE [] END"):
    """Update the local variables representing the current state of the game from the given state.

    Args:
        state (str): The normalized state of the game. Defaults to "STATE [] END".
    """
    
    global PLAYERS
    
    messages = state.split(" ")
    if len(messages) == 3 and messages[0] == "STATE" and messages[2] == "END":
        print(messages[1])
        PLAYERS = Player.toPlayers(messages[1])
        print(PLAYERS)



def exit():
    """Send the normalized disconnection request and then exits the game.
    """
    
    global CONNECTED
    
    t = time.time()
    while time.time() - t < DISCONNECTION_WAIT:
        if send("DISCONNECTION " + USERNAME + " END") == "DISCONNECTED " + USERNAME + " END":
            break
    
    CONNECTED = False
    #sys.exit()



def main():
    """Main function launching the parallel threads to play the game and communicate with the server.
    """
    
    global CONNECTED
    
    while not CONNECTED:
        CONNECTED = connect()
        time.sleep(WAITING_TIME)
    
    pg.init()
    
    global SCREEN
    SCREEN = pg.display.set_mode(SIZE)
    
    gameUpdater = Thread(target=game)
    displayer = Thread(target=display)
    
    gameUpdater.start()
    displayer.start()



# ----------------------- Client Side -----------------------

if __name__ == "__main__":
    
    print("Which username do you want to use ? (By default, it is " + USERNAME + ")")
    username = input()
    
    if username != "":
        USERNAME = username
    
    main()
