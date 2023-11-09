
# ----------------------- Imports -----------------------

from socket import *
from random import randint

from threading import *
import time

from player import Player
from wall import Wall

# ----------------------- IP -----------------------

def extractingIP():
    s = socket(AF_INET, SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    IP = s.getsockname()[0]
    s.close()
    return(IP)


# ----------------------- Constants-----------------------
SIZE_X = 1000
SIZE_Y = 1000
SIZE = (SIZE_X,SIZE_Y)

STEP_X = 15
STEP_Y = 15

IP = extractingIP()

SIZE_MAX_PSEUDO = 10



# Maybe not mandatory
WAITING_TIME = 0.0001 # in seconds - period of connection requests when trying to connect to the host

HOST = str(IP)
PORT = 9998

MAINSOCKET = None
BACKLOG = 1
dicoSocket = {}
waitingConnectionList = []
waitingDisconnectionList = []


LISTENING = True
MANAGING = True
STOP = False

# ----------------------- Variables -----------------------
dicoJoueur = {} # Store players' Player structure

dicoMur = {}
dicoMur[0] = Wall(0, (50, 50, 50), (150, 800), (200, 50))
dicoMur[1] = Wall(1, (30, 30, 30), (850, 100), (10, 500))
dicoMur[2] = Wall(2, (30, 30, 30), (450, 100), (400, 10))

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
    return(states())

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


def states():
    liste = []
    for key in dicoJoueur:
        ip, username, color, (x, y), (dx, dy) = dicoJoueur[key].toList()
        liste.append((username,color,(x,y),(dx,dy))) 
    out = "STATE " + (str(liste)).replace(" ","") + " END"
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
    return(SIZE_X/10,SIZE_Y/10)

def positionNewPlayer(dx, dy):
    return(randint(0, int(SIZE_X - dx)), randint(0, int(SIZE_Y - dy)))

def colorNewPlayer():
    return((randint(1,255),randint(1,255),randint(1,255)))


# ----------------------- Threads -----------------------
def manage_server():
    global STOP
    global LISTENING
    global MANAGING
    
    global MAINSOCKET
    
    while not STOP:
        command = input()
        match command:
            case "stop":
                STOP = True
                print("STOP = ", STOP)
                MAINSOCKET.shutdown(SHUT_RDWR)
                MAINSOCKET.close()
                
                print("Socket server closed !")
                
                for (username,(sock,addr)) in dicoSocket:
                    sock.shutdown(SHUT_RDWR)
                    sock.close()
                
                print("Client sockets closed !")
            case "deaf":
                LISTENING = False
                print("LISTENING = ", LISTENING)
            case "listen":
                LISTENING = True
                print("LISTENING = ", LISTENING)
            case "ignore":
                MANAGING = False
                print("MANAGING = ", MANAGING)
            case "manage":
                MANAGING = True
                print("MANAGING = ", MANAGING)
            case _:
                print("Wrong command : use either stop, deaf, listen, ignore, manage")
                print("STOP = ", STOP)
                print("LISTENING = ", LISTENING)
                print("MANAGING = ", MANAGING)
                
def listen_new():
    global STOP
    global LISTENING
    
    global waitingConnectionList
    
    while not STOP:
        while LISTENING:
            sock, addr = MAINSOCKET.accept()
            data = sock.recv(1024).strip()
            
            in_ip = addr[0]
            
            print("{} wrote:".format(in_ip))
            in_data = str(data,'utf-16')
            print(in_data)
            
            out = processRequest(in_ip ,in_data)
            message = out.split(' ')
            
            if message[0]=="CONNECTED":
                username = message[1]
                waitingConnectionList.append((username, sock, addr))

            print(">>> ",out,"\n")
            sock.sendall(bytes(out,'utf-16'))
            
            time.sleep(WAITING_TIME)

def listen_old():
    global STOP
    global MANAGING
    
    global waitingConnectionList
    global waitingDisconnectionList
    
    while not STOP:
        while MANAGING:
            coSocketList = waitingConnectionList.copy()
            waitingConnectionList = []
            
            for elt in coSocketList:
                username, sock, addr = elt[0], elt[1], elt[2]
                dicoSocket[username] = sock, addr
            

            
            diSocketList = waitingDisconnectionList.copy()
            waitingDisconnectionList = []
            
            for elt in diSocketList:
                username, sock, addr = elt[0], elt[1], elt[2]
                dicoSocket.pop(username)
                
                sock.close()


            
            for username in dicoSocket:
                sock = dicoSocket[username][0]
                addr = dicoSocket[username][1]

                data = sock.recv(1024).strip()
                
                in_ip = addr[0]
                
                print("{} wrote:".format(in_ip))
                in_data = str(data,'utf-16')
                print(in_data)
                
                out = processRequest(in_ip ,in_data)
                message = out.split(" ")
                        
                if message[0]=="DISCONNECTED":
                    username = message[1]
                    waitingDisconnectionList.append((username, sock, addr))
                
                print(">>> ",out,"\n")
                sock.sendall(bytes(out,'utf-16'))
                
            time.sleep(WAITING_TIME)
    


# ----------------------- Main -----------------------
def main():
    global MAINSOCKET
    
    # Initialization
    if MAINSOCKET == None:
        MAINSOCKET = socket(AF_INET, SOCK_STREAM)
        MAINSOCKET.bind((HOST, PORT))
        MAINSOCKET.listen(BACKLOG)
    
    print("Server opened with :\n    - ip = " + str(IP) + "\n    - port = " + str(PORT))
    
    listener_new = Thread(target=listen_new)
    manager_server = Thread(target=manage_server)
    listener_old = Thread(target=listen_old)
    
    listener_new.start()
    manager_server.start()
    listener_old.start()

if __name__ == "__main__":
    main()
