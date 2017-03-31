import sys
import socket
import time
import threading

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

class ConBot:
    def __init__(self, server, name, channel, port, secret):
        self._server = server
        #need to generate nick
        self._nick = name
        self._channel = channel
        self._port = port
        
        self._secret = secret

        self._socket = socket.socket()
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
                    self._nick = self._nick + str(randomint(1, 1000))
                    self.initConnection()
                  

            responses = self.logRecv()

    

if __name__ == "__main__":

    if len(sys.argv) != 5:
        eprint("Invalid usage. Usage: ")
        eprint("python3 conbot.py <hostname> <port> <channel> <secret-phrase>")
    else:

        host = sys.argv[1]
        name = "leeroy_jenkins"
        port = sys.argv[2]
        chan = sys.argv[3]
        secret = sys.argv[4]

        bot = ConBot("172.19.2.91", "leeroy_jenkins", "#channel1", 6667, secret)
        bot.doWork()
        eprint("Shutting Down...")
