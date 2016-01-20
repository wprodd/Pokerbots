import random

class BBHistorian:
    #BB goes first post flop
    def __init__(self):
        self.numPreFlopActions = 0
        self.preFlopRaiseCount = 0 #number of times opponent raises pre-flop
        self.preFlopRaiseProportion = 0.0 #expected pre-flop raise (as a fraction of the pot) given that opponent raises
        self.limp = 0.0 #probability of limping
        self.foldToPreFlopRaise = 0.0
        self.timesRaised = 0
        self.currentStage = 0
    def update(self, pot, currentStage, action):
        details = action.split(":")
        if(currentStage == 0):
            if(details[0] == 'RAISE' or details[0] == 'BET'):
                self.preFlopRaiseProportion = (self.preFlopRaiseProportion*self.numPreFlopActions + (float(details[1])/pot))/(self.numPreFlopActions + 1)
                self.preFlopRaiseCount = self.preFlopRaiseCount + 1
            if(details[0] == 'CALL'):
                self.limp = (self.limp*self.numPreFlopActions + 1.0)/(self.numPreFlopActions + 1)
            else:
                self.limp = (self.limp*self.numPreFlopActions)/(self.numPreFlopActions + 1)
            self.numPreFlopActions = self.numPreFlopActions + 1
        """if(details[0] == 'RAISE' or details[0] == 'BET'):
            if(int(details[1]) == pot/3):
                self.preFlopThreeTimesRaise = self.preFlopThreeTimesRaise + 1"""
        if(self.currentStage != currentStage):
            self.timesRaised = 0
        self.currentStage = currentStage
    def raised(): #call when this bot actually raises
        self.timesRaised = self.timesRaised + 1
    def exploitProbability(self, pot, currentStage, legalActions, lastActions):
        outThreshold = [10, 15, 17, 19]
        betThreshold = [20, 30, 40, 50]
        can = {"BET": False, "RAISE": False, "CALL": False, "CHECK": False, "FOLD": False}
        minBet = 0
        maxBet = 0
        for action in legalActions:
            details = action.split(':')
            if details[0]=='RAISE':
                can["RAISE"] = True
                minBet = details[1]
                maxBet = details[2]
            elif details[0]=='BET':
                can["BET"] = True
                minBet = details[1]
                maxBet = details[2]
            else:
                can[details[0]] = True
        prob = {"BET": 0.0, "RAISE": 0.0, "CALL": 0.0, "CHECK": 0.0, "FOLD": 0.0}
        for k in can.keys():
            if(can[k]):
                prob[k] = 1.0
        prob["FOLD"] = 0.0
        lastDetails = lastActions[0].split(':')
        if(len(lastActions) > 0 and (lastDetails[0] == 'BET' or lastDetails[1] == 'RAISE')):
            prob["FOLD"] = 1.0
        if(currentStage == 0):
            if(len(lastActions) > 0 and lastDetails[0] == 'CALL'):
                prob["BET"] = prob["BET"]*(1.0/(self.limp + 0.01))
                #prob["CHECK"] = prob["CHECK"]*(1.0 - (1.0/(self.limp + 0.01)))
            elif(len(lastActions) > 0 and (lastDetails[0] == 'BET' or lastDetails[1] == 'RAISE')):
                preFlopRaiseProb = float(self.preFlopRaiseCount)/self.numPreFlopActions
                proportion = float(lastDetails[1])/pot
                prob["RAISE"] = prob["RAISE"]*preFlopRaiseProb*(10.0**(self.preFlopRaiseProportion - proportion))
                prob["FOLD"] = 0.5
                if(proportion >= self.preFlopRaiseProportion):
                    prob["FOLD"] = prob["FOLD"]*(1.0 - preFlopRaiseProb)*(10.0**(proportion - self.preFlopRaiseProportion))
                prob["CALL"] = prob["CALL"] + (1.0 - (1.2**(-1*timesRaised)))*prob["RAISE"];
                prob["RAISE"] = prob["RAISE"]*(1.2**(-1*timesRaised))
        """if(handValue < outThreshold[currentStage]):
            if(can["CHECK"]):
                prob["CHECK"] = 1.0
            else:
                prob["FOLD"] = 1.0
        else:
            if(can["RAISE"] and handValue >= betThreshold[currentStage]):
                prob["RAISE"] = 2.0**(-1*timesRaised)
            if(can["CALL"]):
                prob["CALL"] = 1.0 - prob["RAISE"]
            if(can["CHECK"]):
                prob["CHECK"] = 1.0 - prob["RAISE"]
            if(currentStage == 0):
                lastOpponent = lastActions[0].split(':')
                if(lastOpponent[0] == 'RAISE'):
                    if(int(lastOpponent[1]) == pot/3):
                        preFlopProb = float(preFlopThreeTimesRaise)/float(numHands)
                        prob["CALL"] = prob["CALL"] + 2.0**(0.3/(preFlopProb + 0.01)) #replace with ev stuff later
                        prob["FOLD"] = prob["FOLD"] + 1.0 - 2.0**(0.3/(preFlopProb + 0.01)) #replace with ev stuff later"""
        sum = 0.0
        for p in prob.values():
            sum = sum + p
        for k in prob.keys():
            prob[k] = float(prob[k])/sum
        return prob
