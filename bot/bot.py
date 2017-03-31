import socket
import time
import threading
import random
import sys
import traceback

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

class Bot:
    def __init__(self, server, channel, port, secret):
        """ """
        self._server = server
        self._channel = "#" + channel
        self._port = port
        self._nick = ""
        self._secret = secret
        
        self.pickNewName()

        try: 
            self._socket = socket.socket()
            self._socket.connect((server, port))

            eprint("!! Connected to server {0} on port {1}".format(server, port))
            eprint("!! Bot attempting to register for server with nickname {0}".format(self._nick))
            
            self.doWork()
        except:
            eprint("!! Error connecting to channel {0} server {1} on port {2}".format(self._channel, self._server, self._port))
            eprint(traceback.format_exc())

            
    def parsemsg(self, s):
        """Breaks a message from an IRC server into its prefix, command, and arguments.
        """
        prefix = ''
        trailing = []
        if not s:
            raise IRCBadMessage("Empty line.")
        if s[0] == ':':
            prefix, s = s[1:].split(' ', 1)
        if s.find(' :') != -1:
            s, trailing = s.split(' :', 1)
            args = s.split()
            args.append(trailing)
        else:
            args = s.split()
            
        command = args.pop(0)
            
        return prefix, command, args

    def logSend(self, msg):
        msg = bytes(msg)
        print("--> sending: " + str(msg))
        self._socket.send(msg)
        
    def logRecv(self):
        response = self._socket.recv(1024).decode("utf-8")
        print("<-- received: " + str(response))
        responses = response.split("\r\n")
        return responses[:len(responses) - 1]

    def initConnection(self):
        self.logSend("NICK {}\r\n".format(self._nick).encode("utf-8"))

        ##change this to be a randomized name per bot, note nick is their identifying feature,
        ## not the name
        self.logSend("USER {0} 0 * :{1}\r\n".format(self._nick, self._nick).encode("utf-8"))
        self.logSend("JOIN {}\r\n".format(self._channel).encode("utf-8"))

    def debugLogResponse(self, prefix, command, args):
        """ """
        print("prefix: {0}".format(prefix))
        print("command: {0}".format(command))
        print("args: {0}".format(args))


    def doWork(self):
        """ """
        self.initConnection()

        responses = self.logRecv()
        while responses:
            for response in responses:
                prefix, command, args = self.parsemsg(response)

                self.debugLogResponse(prefix, command, args)
                
                if command == "PING":
                    self.logSend("PONG {0}\r\n".format(args[0]).encode("utf-8"))
                elif command == "433":
                    #username taken
                    self.pickNewName()
                    self.initConnection()
            

            responses = self.logRecv()

    def pickNewName(self):
        """ set new name """
        first = ["commander", "prince", "princess", "lord", "king", "queen", "mr", "keeper", "warden", "governor", "mayor", "president"]
        middle = ["toad", "pie", "skillet", "cake", "hamster", "jock", "rage", "fun", "gander", "goose", "bug", "turkey", "pork"]
        last = ["toes", "fingers", "chef", "herder", "chop", "shepherd", "buns", "pickle", "fiend", "burger", "milk", "juice"]

        firstInd = random.randint(0, len(first) - 1)
        middleInd = random.randint(0, len(middle) - 1)
        lastInd = random.randint(0, len(last) - 1)

        #change this to a new server
        self._nick = first[firstInd] + "_" + middle[middleInd] + "_" + last[lastInd]


if __name__ == "__main__":
    if len(sys.argv) != 5:
        eprint("Invalid usage. Use:")
        eprint("python {0} [hostname] [port] [channel] [secret_phrase]".format(sys.argv[0]))
    else:
        try:
            server = str(sys.argv[1])
            port = int(sys.argv[2])
            channel = str(sys.argv[3])
            secret = str(sys.argv[4])

            bot = Bot(server, channel, port, secret)
        except ValueError:
            eprint("Invalid port number. Port must be from 1-65535")
        except:
            eprint("An error occurred. Please ensure valid parameters.")
        finally:
            eprint("Exitting bot...")
            
    
    #bot = Bot("127.0.0.1", "#channel1", 6667)
