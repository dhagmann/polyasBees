from random import random, randint, uniform
from joblib import Parallel, delayed
import itertools, win32api, win32process, win32con

repetitions = 100000
simType = "discovery"

if simType == "discovery":
    globalBalls = ((0, 0),)
    globalIncrease = (((2,),(1,),),)
    probPop = [0, 0.1, 0.5, 1]
    discoveryRate = [0.5,]
    discoveryRateOptimal = [0.1,]
    recruitmentRate = [0.5]

outputFile = simType + "3.csv"

numAttributes = len(globalIncrease[0][0])
def main():
    T = [x for x in range(5,76,1)]
    L = list(itertools.product(probPop, T, globalBalls, globalIncrease, discoveryRate, discoveryRateOptimal, recruitmentRate))
    results = Parallel(n_jobs=-1, verbose=500000, pre_dispatch='all')(delayed(iteration)(cross, repetitions) for cross in L)    
    
    ### Write File ###
    headers = 'probPopping,threshold,numChoices,share1,share2,time,noResolution,startingContents,increaseRates,discoveryRate,discoveryRateOptimal,recruitmentRate\n' 
    with open(outputFile, 'w') as f: 
        f.write(headers)
        f.write('\n'.join('%s,%s,%s,%s,%s,%s,%s,"%s","%s",%s,%s,%s' % x for x in results))

def iteration(cross, repetitions):
    pid = win32api.GetCurrentProcessId()
    handle = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, True, pid)
    win32process.SetPriorityClass(handle, win32process.IDLE_PRIORITY_CLASS)
    probPop, T, iterationBalls, iterationIncrease, discoveryRate, discoveryRateOptimal, recruitmentRate = cross
    count, count2, time, noResolution = 0, 0, 0, 0

    for i in range(repetitions):
        # Set up new iteration
        balls = list(iterationBalls)
        increase = list(iterationIncrease)
        numTargets = len(balls)
        # Run iteration
        simulation = playGame(balls,T, increase, probPop, discoveryRate, discoveryRateOptimal, recruitmentRate)
        # Record Results
        if simulation["index"] == 0:
            count +=1
        if simulation["index"] == 1:
            count2 += 1
        time = time+simulation["time"]
        noResolution += simulation["noResolution"]
        if repetitions == noResolution:
            avgTime = 0
        else:
            avgTime = time/(repetitions - noResolution)
    # Return results for output file
    optimal = count/repetitions
    optimal2 = count2/repetitions
    return probPop, T, numTargets, optimal, optimal2, avgTime, noResolution, iterationBalls, iterationIncrease, discoveryRate, discoveryRateOptimal, recruitmentRate

def drawBalls(balls, increase):
    ''' list -> int
        Takes as input a list with balls in the urn, 
        then returns a new list with one additional ball.
    '''
    rnd = randint(1, sum(balls))
    index = 0
    while sum(balls[0:index+1]) < rnd:
        index +=1
        if index > len(balls):
            print("Error!")
            break
    balls[index] += increase[index][int(random()//(1/numAttributes))]
    return balls
     
def popBalls(balls):
    # One ball is selected at random and pops.
    rnd = randint(1, sum(balls))
    index = 0
    while sum(balls[0:index+1]) < rnd:
        index += 1
    balls[index] = balls[index]-1
    return balls

def playGame(balls, T, increase, probPop, discoveryRate, discoveryRateOptimal, recruitmentRate):
    time = 0
    count = 0
    while max(balls) < T:
        chooseAction = uniform(0, probPop + discoveryRate + recruitmentRate)
        if chooseAction < probPop:
            if sum(balls) != 0:
                balls = popBalls(balls)
        elif chooseAction < probPop + discoveryRate:
            if uniform(0,1) < discoveryRateOptimal:
                balls[0] += 1
            else:
                balls[1] += 1
        elif chooseAction <= probPop + discoveryRate + recruitmentRate:
            if sum(balls) != 0:
                balls = drawBalls(balls, increase)
        else:
            print("ERROR! No Action Chosen!")
        time += incrementTime(balls, discoveryRate, recruitmentRate, probPop)
        count += 1
        if count >= 100000:
            return{"index":-99, "time":0, "noResolution":1}
    return{"index":balls.index(max(balls)), "time":time, "noResolution":0}

def incrementTime(balls, discoveryRate, recruitmentRate, probPop):
    increment = 1/(sum(balls)*(recruitmentRate + probPop) + discoveryRate)
    return increment

if __name__ == "__main__":
    main()