import socket
import time
import threading


class Bot:
    def __init__(self, server, name, channel, port):
        """ """
        self._server = server
        self._nick = name
        self._channel = channel
        self._port = port

        self._socket = socket.socket()
        self._socket.connect((server, port))
        
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
        print("sending: " + msg)
        self._socket.send(msg)
        
    def logRecv(self):
        response = self._socket.recv(1024).decode("utf-8")
        print("received: " + response)
        responses = response.split("\r\n")
        return responses[:len(responses) - 1]

    def initConnection(self):
        self.logSend("NICK {}\r\n".format(self._nick).encode("utf-8"))

        ##change this to be a randomized name per bot, note nick is their identifying feature,
        ## not the name
        self.logSend("USER {0} 0 * :tyriggitybiggity".format(self._nick).encode("utf-8"))
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
                    self.logSend("PONG {}\r\n".format(args[0].encode("utf-8")))
                elif command == "433":
                    #username taken
                    self.pickNewName()
                    self.initConnection()
            

            responses = self.logRecv()

    def pickNewName(self):
        """ set new name """
        #change this to a new server
        self._name = "butts"


if __name__ == "__main__":
    bot = Bot("127.0.0.1", "tyrone", "#channel1", 6667)


'''
s.send("JOIN {}\r\n".format(CHAN).encode("utf-8"))

print("Connected to IRC...")

while True:
    response = s.recv(1024).decode("utf-8")
    if response == "PING :tmi.twitch.tv\r\n":
        s.send("PONG :tmi.twitch.tv\r\n".encode("utf-8"))
    else:
        (prefix, command, args)= parsemsg(response)
        print("prefix: " + prefix)
        print("command: " + command)
        for p in args: print ("arg["+p.strip()+"]") 
        if command == "PRIVMSG":
              if args[0] == CHAN and args[1].strip() == "!saysomething":
                    s.send("PRIVMSG {} :Im a new message\r\n".format(CHAN).encode("utf-8"))
                    print("PRIVMSG {} :Im a new message\r\n".format(CHAN).encode("utf-8"))
              if args[0] == CHAN and args[1].strip() == "!quit":
                    s.send("PRIVMSG {} :cpsc526bot out!\r\n".format(CHAN).encode("utf-8"))
                    print(NICK + " out!")
                    break
        print(response)
s.close()
#sleep(1 / cfg.RATE)
'''
