import argparse
import socket
import sys

"""
Simple example pokerbot, written in python.

This is an example of a bare bones pokerbot. It only sets up the socket
necessary to connect with the engine and then always returns the same action.
It is meant as an example of how a pokerbot should communicate with the engine.
"""
class Player:
    def stuff():
        return 0
    def run(self, input_socket):
        # Get a file-object for reading packets from the socket.
        # Using this ensures that you get exactly one packet per read.
        f_in = input_socket.makefile()
        while True:
            # Block until the engine sends us a packet.
            data = f_in.readline().strip()
            # If data is None, connection has closed.
            if not data:
                print "Gameover, engine disconnected."
                break

            # Here is where you should implement code to parse the packets from
            # the engine and act on it. We are just printing it instead.
            
            dataList = data.split()
            dataType = dataList[0]
            print data
            if dataType=="NEWGAME":
                myBank = dataList[3]
                oppBank = dataList[3]
                totalHands = dataList[5]
                bb = dataList[4]
                timeRemaining = dataList[6]
            if dataType=="NEWHAND":
                handId = dataList[1]
                button = dataList[2]
                myHand = [dataList[3],dataList[4],dataList[5],dataList[6]]
                myBank = dataList[7]
                oppBank = dataList[8]
                timeRemaining = dataList[9]
                handValue = handEvaluator(myHand)
                print myHand

            # When appropriate, reply to the engine with a legal action.
            # The engine will ignore all spurious responses.
            # The engine will also check/fold for you if you return an
            # illegal action.
            # When sending responses, terminate each response with a newline
            # character (\n) or your bot will hang!
            if dataType == "GETACTION":
                pot = dataList[1]
                #Reads board cards into a list
                boardCards = []
                numCards = int(dataList[2])
                for card in range(3,numCards+3):
                    boardCards.append(dataList[card])
                print boardCards

                #Read lastActions into a list
                lastActions = []
                numLastActionsIndex = int(dataList[2])+3
                numLastActions = int(dataList[numLastActionsIndex])
                for action in range(numLastActionsIndex+1,numLastActionsIndex+numLastActions+1):
                    lastActions.append(dataList[action])
                print lastActions

                #Read legalActions into a list
                legalActions = []
                numLegalActionsIndex = numLastActionsIndex+numLastActions+1
                numLegalActions = int(dataList[numLegalActionsIndex])
                for action in range(numLegalActionsIndex+1,numLegalActionsIndex+numLegalActions+1):
                    print action
                    legalActions.append(dataList[action])
                print legalActions
                timeRemaining = dataList[-1]
                if (not button and handEvaluator(myHand)>outThreshold) or (handEvaluator(myHand)>inThreshold):
                    
                s.send("FOLD\n")
            elif dataType == "REQUESTKEYVALUES":
                # At the end, the engine will allow your bot save key/value pairs.
                # Send FINISH to indicate you're done.
                s.send("FINISH\n")
        # Clean up the socket.
        s.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='A Pokerbot.', add_help=False, prog='pokerbot')
    parser.add_argument('-h', dest='host', type=str, default='localhost', help='Host to connect to, defaults to localhost')
    parser.add_argument('port', metavar='PORT', type=int, help='Port on host to connect to')
    args = parser.parse_args()

    # Create a socket connection to the engine.
    print 'Connecting to %s:%d' % (args.host, args.port)
    try:
        s = socket.create_connection((args.host, args.port))
    except socket.error as e:
        print 'Error connecting! Aborting'
        exit()

    bot = Player()
    bot.run(s)
