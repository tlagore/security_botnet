import socket
import time

HOST = "irc.twitch.tv"              # the Twitch IRC server
PORT = 6667                         # always use port 6667!
NICK = "someonespecialll"            # your Twitch username, lowercase
PASS = "oauth:wv4u9nem3b330zkh4kvdjobvjn9e2x" # your Twitch OAuth token
CHAN = "#someonespecialll"                   # the channel you want to join


def parsemsg(s):
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


# network functions go here

s = socket.socket()
s.connect((HOST, PORT))
s.send("PASS {}\r\n".format(PASS).encode("utf-8"))
s.send("NICK {}\r\n".format(NICK).encode("utf-8"))
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
