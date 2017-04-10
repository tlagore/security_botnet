# CPSC 526 Assignment 5 - netsec botnet

CPSC 526 - Network Security - Winter 2017

Assignment 5

# Authors

Tyrone Lagore T01 (10151950) James MacIsaac T03 (10063078)

# Desc

A simulation of a botnet with a controller, an IRC for bot/controller intercommunication, and a set of bot clients.
The Controller will check the IRC server for available bots and issue global commands to all at once.

# Running the program

## Controller:
  Can be found in the conbot folder in the project directory. To run it:
    python3 conbot.py hostname port channel secret-phrase [debug]
    
    - Host and port refer to the IRC server to connect to
    - Channel is the irc channel to conenct to
    - Secret-phrase is the secret phrase that will authenticate the controller to the bots
    - Debug is optional an logs debugging output
 
 Commands:
    The controller can run these commands:
    - status - report status of how many bots are in the channel currently.
    - attack <host> <port> - tells the bots to perform an attack on the given host/port. 
                           - will display the attack number of their session to the attackee 
    - move <host> <port> <channel> - moves the bots to a different host/port/channel that
                                      corresponds to an irc server
    - quit - shuts down the controller. bots remain unaffected.
    - shutdown - sends a shutdown comamnd to all bots. controller remains unaffected.
    - actnatural - Tells the bots to act 'naturally' in the irc chat channel as users
                    of a twitch chat would!
## Bot:
  Can be found in the bot folder in the project directory. To run it:
    python3 bot.py hostname port channel secret_phrase
    
    - Host and port refer to the IRC server to connect to
    - Channel is the irc channel to conenct to
    - Secret-phrase is the secret phrase that will authenticate the controller to the bots
    
  The bots sit awaiting commands from the controller bot account. The controller will broadcast
  a trigger phrase in the channel which the bots will respond to with a specific phrase to authenticate. 
  After this, the secret-phrase is sent with each command to make sure that bots only respond to their controller.

  
     
