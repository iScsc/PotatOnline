
# ----------------------- Imports -----------------------

import socketserver
import socket
from random import randint

from player import Player

from light import Light
from inlight import *
from wall import Wall

# ----------------------- IP -----------------------

def extractingIP():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    IP = s.getsockname()[0]
    s.close()
    return(IP)


# ----------------------- Constants-----------------------
# Game map
SIZE_X = int(1920 * .9)
SIZE_Y = int(1080 * .9)
SIZE = (SIZE_X,SIZE_Y)

STEP_X = 3
STEP_Y = 3

# Server
IP = extractingIP()

# Player
SIZE_MAX_PSEUDO = 10

PLAYER_SIZE = (20, 20)

# ----------------------- Variables -----------------------
dicoJoueur = {} # Store players' Player structure

dicoMur = {}
dicoMur[-1] = Wall(-1, (50, 50, 50), (350, 575), (225, 10))
dicoMur[0] = Wall(0, (50, 50, 50), (150, 800), (200, 10))
dicoMur[1] = Wall(1, (50, 50, 50), (350, 500), (10, 310))
dicoMur[2] = Wall(2, (50, 50, 50), (250, 500), (100, 10))

dicoMur[3] = Wall(3, (30, 30, 30), (850, 100), (10, 450))
dicoMur[4] = Wall(4, (30, 30, 30), (450, 100), (400, 10))

dicoMur[5] = Wall(5, (30, 30, 30), (75, 100), (275, 10))
dicoMur[6] = Wall(6, (30, 30, 30), (75, 50), (10, 200))

dicoMur[7] = Wall(7, (30, 30, 30), (325, 250), (150, 10))

dicoMur[8] = Wall(8, (30, 30, 30), (850, 650), (10, 250))
dicoMur[9] = Wall(9, (30, 30, 30), (650, 800), (550, 10))
dicoMur[10] = Wall(10, (30, 30, 30), (850, 950), (10, 250))

dicoMur[11] = Wall(11, (30, 30, 30), (1400, 800), (200, 10))
dicoMur[12] = Wall(12, (30, 30, 30), (1600, 300), (10, 510))
dicoMur[13] = Wall(13, (30, 30, 30), (1400, 225), (200, 10))
dicoMur[14] = Wall(14, (30, 30, 30), (1400, 225), (10, 510))

dicoMur[15] = Wall(15, (30, 30, 30), (1400, 625), (150, 10))
dicoMur[16] = Wall(16, (30, 30, 30), (1450, 400), (150, 10))

dicoMur[17] = Wall(17, (30, 30, 30), (1150, 0), (10, 350))
dicoMur[18] = Wall(18, (30, 30, 30), (1000, 450), (310, 10))

# -------------------- Processing a Request -----------------------
def processRequest(ip, s):
    type = typeOfRequest(s)
    if type == "CONNECT":
        return(processConnect(ip, s))
    elif type == "INPUT":
        return(processInput(ip, s))
    elif type == "DISCONNECTION":
        return(processDisconection(ip, s))
    else :
        return("Invalid Request")

def processConnect(ip, s):
    pseudo = extractPseudo(s)
    if validPseudo(pseudo):
        return("This Pseudo already exists")
    elif len(pseudo)>SIZE_MAX_PSEUDO:
        return("Your pseudo is too big !")
    elif " " in pseudo:
        return("Don't use ' ' in your pseudo !")
    else :
        initNewPlayer(ip, pseudo)
        return(firstConnection(pseudo))
    
def processInput(ip, s):
    pseudo = extractPseudo(s)
    if not(validPseudo(pseudo)):
        return("No player of that name")
    if not(validIp(ip, pseudo)):
        return("You are impersonating someone else !")
    inputLetter = extractLetter(s,pseudo)
    Rules(inputLetter,pseudo)
    return(states(pseudo))

def processDisconection(ip, s):
    pseudo = extractPseudo(s)
    if not(validIp(ip, pseudo)):
        return("You are impersonating someone else !")
    dicoJoueur.pop(pseudo)
    return("DISCONNECTED" + s[13:])


def typeOfRequest(s):
    type = ""
    i = 0
    n = len(s)
    while i<n and s[i]!=" ":
        type+=s[i]
        i+=1
    return(type)

def extractPseudo(s):
    pseudo = ""
    n = len(s)
    i0 = len(typeOfRequest(s)) + 1
    i = i0
    while i<n and s[i]!=" ":
        pseudo+=s[i]
        i+=1
    return(pseudo)

def extractLetter(s,pseudo):
    n = len(pseudo)
    return(s[7 + n])


def dummyLights():
    l00 = Light((0,0))
    #l10 = Light((SIZE_X,0))
    #l11 = Light((SIZE_X,SIZE_Y))
    #l01 = Light((0,SIZE_Y))
    return([l00])#,l10,l11,l01])    

def states(pseudo):
    player = 0
    liste = []
    listeOfPlayer = []
    listOfLight = dummyLights()
    for key in dicoJoueur:
        p =  dicoJoueur[key]
        if key == pseudo:
            player = p
        listeOfPlayer.append(p)
    
    shadows = Visible(p,listOfLight,listeOfPlayer,SIZE_X,SIZE_Y)
    visiblePlayer = allVisiblePlayer(shadows,listeOfPlayer)
    formatshadows = sendingFormat(shadows)
    
    for key in visiblePlayer:
        p = dicoJoueur[key]
        liste.append((key,p.color,p.position,p.size)) 
    out = "STATE "+(str(liste)).replace(" ","")+" SHADES "+formatshadows+" END"

    return(out)

def walls():
    liste = []
    for key in dicoMur:
        id, color, (x, y), (dx, dy) = dicoMur[key].toList()
        liste.append((id,color,(x,y),(dx,dy)))
    out = "WALLS " + (str(liste)).replace(" ","") + " END"
    return(out)

def firstConnection(pseudo):

    out = "CONNECTED " + pseudo + " " + (str(SIZE)).replace(" ","") + " " + walls().replace("END","") + states()
    return(out)

def validPseudo(pseudo):
    return(pseudo in dicoJoueur.keys())

def validIp(ip, pseudo):
    return (pseudo in dicoJoueur.keys() and dicoJoueur[pseudo].ip == ip)


# ----------------------- Games Rules -----------------------

def Rules(inputLetter,pseudo):

    ip, username, color, (x, y), (dx, dy) = dicoJoueur[pseudo].toList()

    match inputLetter:
        case ".": #nothing
            #x+=randint(-1,1)
            #y+=randint(-1,1)
            pass
        case "R":
            x+=STEP_X
        case "L":
            x-=STEP_X
        case "U":
            y-=STEP_Y
        case "D":
            y+=STEP_Y
        case "T":
            x,y = positionNewPlayer()
        case _ :
            return("Invalid Input")

    if correctPosition(pseudo, x,y,dx,dy):
        dicoJoueur[pseudo].update(position=(x, y), size=(dx, dy))
    return()

def correctPosition(pseudo, x,y,dx,dy):
    correctX = (x>=0) and (x+dx <= SIZE_X)
    correctY = (y>=0) and (y+dy <= SIZE_Y)
    
    return correctX and correctY and not collision(pseudo, x, y, dx, dy)

def collision(pseudo, x, y ,dx ,dy):
    
    c = (x + dx/2, y + dy/2)
    
    for key in dicoMur.keys():
        id, color, (wx, wy), (wdx, wdy) = dicoMur[key].toList()
        
        if abs(c[0] - wx - wdx/2) < (dx + wdx)/2 and abs(c[1] - wy - wdy/2) < (dy + wdy)/2:
            return True
    
    for key in dicoJoueur.keys():
        if key != pseudo:
            ip, username, color, (px, py), (pdx, pdy) = dicoJoueur[key].toList()
            
            if abs(c[0] - px - pdx/2) < (dx + pdx)/2 and abs(c[1] - py - pdy/2) < (dy + pdy)/2:
                return True
    
    return False



# ----------------------- Init of a new Player -----------------------


def initNewPlayer(ip, pseudo):
    dx,dy = sizeNewPlayer()
    
    x,y = positionNewPlayer(dx, dy)
    
    while not correctPosition(pseudo, x, y, dx, dy):
        x, y = positionNewPlayer(dx, dy)
    
    color = colorNewPlayer()
    dicoJoueur[pseudo] = Player(ip, pseudo, color, (x, y), [dx, dy])

def sizeNewPlayer():
    return PLAYER_SIZE

def positionNewPlayer(dx, dy):
    return(randint(0, int(SIZE_X - dx)), randint(0, int(SIZE_Y - dy)))

def colorNewPlayer():
    return((randint(1,255),randint(1,255),randint(1,255)))



# ----------------------- Handler -----------------------

class MyTCPHandler(socketserver.BaseRequestHandler):
    """
    The request handler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def handle(self):
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(1024).strip()
        
        in_ip = self.client_address[0]
        
        print("{} wrote:".format(in_ip))
        in_data = str(self.data,'utf-16')
        print(in_data)
        
        out = processRequest(in_ip ,in_data)

        print(">>> ",out,"\n")
        self.request.sendall(bytes(out,'utf-16'))



# ----------------------- Main -----------------------

if __name__ == "__main__":
    HOST, PORT = str(IP), 9998
    #HOST, PORT = "localhost", 9998
    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 9999
    with socketserver.TCPServer((HOST, PORT), MyTCPHandler) as server:
        print("HOST = ",IP,"\nPORT = ",PORT,"\n")
        # Activate the server; this will keep running until you
        # interrupt the program with Ctrl-C
        server.serve_forever()