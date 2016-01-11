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
    def handEvaluator(self,hand):
        points = 0
        numRanks = [] #counts number of cards of a particular rank
        for i in range(0, 13):
            numRanks.append(0)
        for s in hand:
            if(s[0] == 'A'):
                numRanks[12] = numRanks[12] + 1
            elif(s[0] == 'K'):
                numRanks[11] = numRanks[11] + 1
            elif(s[0] == 'Q'):
                numRanks[10] = numRanks[10] + 1
            elif(s[0] == 'J'):
                numRanks[9] = numRanks[9] + 1
            elif(s[0] == 'T'):
                numRanks[8] = numRanks[8] + 1
            else:
                numRanks[int(s[0]) - 2] = numRanks[int(s[0]) - 2] + 1
                
        #counting pairs
        if(numRanks[12] == 2):
            points = points + 10000
        if(numRanks[11] == 2):
            points = points + 7
        if(numRanks[10] == 2):
            points = points + 4
        if(numRanks[9] == 2):
            points = points + 2
            
        #counting triples
        if(numRanks[12] == 3):
            points = points + 4
        if(numRanks[11] == 3):
            points = points + 1
        
        #counting four of a kind
        if(numRanks[12] == 4):
            points = points + 1
            
        #counting consecutive numbers
        for i in range(0, 13):
            if(numRanks[i] > 0 and numRanks[(i + 1)%13] > 0):
                points = points + 5*(min(numRanks[i], numRanks[(i + 1)%13]))
        
        numSuits = []
        for i in range(0, 4):
            numSuits.append(0)
        for s in hand:
            if(s[1] == 'c'):
                numSuits[0] = numSuits[0] + 1
            elif(s[1] == 'd'):
                numSuits[1] = numSuits[1] + 1
            elif(s[1] == 'h'):
                numSuits[2] = numSuits[2] + 1
            else:
                numSuits[3] = numSuits[3] + 1
                
        #counting suits
        for i in range(0, 4):
            if(numSuits[i] >= 2):
                points = points + 9 - 2*numSuits[i]
        
        return points
            
    def run(self, input_socket):
        outThreshold = 5
        inThreshold = 2
        betThreshold = 10
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
                handValue = self.handEvaluator(myHand)
                print myHand
                print handValue

            # When appropriate, reply to the engine with a legal action.
            # The engine will ignore all spurious responses.
            # The engine will also check/fold for you if you return an
            # illegal action.
            # When sending responses, terminate each response with a newline
            # character (\n) or your bot will hang!
            if dataType == "GETACTION":
                can = {"BET": False, "RAISE": False, "CALL": False, "CHECK": False, "FOLD": False}
                minBet = 0
                maxBet = myBank
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
                    legalActions.append(dataList[action])
                    if dataList[action][:5]=='RAISE':
                        actionList = dataList[action].split(':')
                        can["RAISE"] = True
                        minBet = actionList[1]
                        maxBet = actionList[2]
                    elif dataList[action][:3]=='BET':
                        actionList = dataList[action].split(':')
                        can["BET"] = True
                        minBet = actionList[1]
                        maxBet = actionList[2]
                    else:
                        can[dataList[action]] = True
                print legalActions
                print can
                timeRemaining = dataList[-1]
                if numCards==0:
                    if ((not button and handValue>=outThreshold) or (handValue>=inThreshold)):
                        if button and handValue>=betThreshold:
                            if can["BET"]:
                                s.send("BET:"+maxBet+"\n")
                            elif can["RAISE"]:
                                s.send("RAISE:"+maxBet+"\n")
                            else:
                                if can["CHECK"]:
                                    s.send("CHECK\n")
                                else:
                                    print "FOLDING"
                                    s.send("FOLD\n")
                        elif not button and handValue<outThreshold:
                            if can["CHECK"]:
                                s.send("CHECK\n")
                            else:
                                s.send("FOLD\n")
                            
                        else:
                            if can["CALL"]:
                                s.send("CALL\n")
                            else:
                                s.send("CHECK\n")
                    else:
                        if can["CHECK"]:
                            s.send("CHECK\n")
                        else:
                            s.send("FOLD\n")
                else:
                    if can["CHECK"]:
                        s.send("CHECK\n")
                    else:
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
