from random import random, randint
from math import floor
from joblib import Parallel, delayed
import itertools, win32api, win32process, win32con

repetitions = 100000
simType = "varyingOptimalPayoff"
# simType = "varyingOptimalPayoff"

if simType == "numTypes":
    globalBalls = ((1, 1), (1, 1, 1), (1, 1, 1, 1))
    globalIncrease = (((2,),(1,), (1,), (1,)),)
    probPop = [0,]
if simType == "ratios":
    globalBalls = ((1, 1, 1),)
    globalIncrease = (((3,),(1,), (1,)), ((3,),(2,), (1,)))
    probPop = [0,]
if simType == "noise":
    globalBalls = ((1, 1),)
    globalIncrease = (((3, 2, 2, 1),(2, 1, 1, 0)), ((2, 2, 2, 2),(1, 1, 1, 1)))
    probPop = [0,]
if simType == "multiAttributesFixed":
    globalBalls = ((1, 1),)
    globalIncrease = (((3, 1), (1, 1)),((2, 2), (1, 1)))
    probPop = [0,]
if simType == "multiAttributesDirectComparison":
    globalBalls = ((1, 1),)
    globalIncrease = (((3, 1), (2, 2)),)
    probPop = [0,]
if simType == "infoCascade":
    globalBalls = ((1, 3),)
    globalIncrease = (((2,), (1,)),)
    probPop = [0, 0.05, 0.10, 0.20]
if simType == "varyingSuboptimalPayoff":
    globalBalls = ((1, 1),)
    globalIncrease = (((4,), (1,)), ((4,), (2,)), ((4,), (3,)))
    probPop = [0,]
if simType == "varyingOptimalPayoff":
    globalBalls = ((1, 1),)
    globalIncrease = (((2,), (1,)), ((3,), (1,)), ((4,), (1,)))
    probPop = [0,]

outputFile = simType + ".csv"

numAttributes = len(globalIncrease[0][0])
def main():
    T = [x for x in range(5,201,1)]
    L = list(itertools.product(probPop, T, globalBalls, globalIncrease))
    results = Parallel(n_jobs=-1, verbose=50000, pre_dispatch='all')(delayed(iteration)(cross, repetitions) for cross in L)    
    
    ### Write File ###
    headers = 'probPopping,threshold,numChoices,share1,share2,time,noResolution,startingContents,increaseRates\n' 
    with open(outputFile, 'w') as f: 
        f.write(headers)
        f.write('\n'.join('%s,%s,%s,%s,%s,%s,%s,"%s","%s"' % x for x in results))

def iteration(cross, repetitions):
    pid = win32api.GetCurrentProcessId()
    handle = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, True, pid)
    win32process.SetPriorityClass(handle, win32process.IDLE_PRIORITY_CLASS)
    probPop, T, iterationBalls, iterationIncrease = cross
    count, count2, time, noResolution = 0, 0, 0, 0

    for i in range(repetitions):
        balls = list(iterationBalls)
        increase = list(iterationIncrease)
        timeNorm = sum(balls)
        numTargets = len(balls)
        simulation = playGame(balls,T, timeNorm, increase, probPop)
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
    
    optimal = count/repetitions
    optimal2 = count2/repetitions
    return probPop, T, numTargets, optimal, optimal2, avgTime, noResolution, iterationBalls, iterationIncrease

def drawBalls(balls, time, timeNorm):
    ''' list -> int
        Takes as input a list with balls in the urn, 
        then returns an index corresponding to the type drawn.
    '''
    rnd = randint(1, sum(balls))
    index = 0
    while sum(balls[0:index+1]) < rnd:
        index +=1
        if index > len(balls):
            print("Error!")
    time += timeNorm/sum(balls)
    return index, time
     
def popBalls(balls, probPop):
    # This code gives each ball an equal
    # probability of popping
    for index in range(len(balls)):
        rnd = [random() for n in range(balls[index])]
        balls[index] -= sum(x <= probPop for x in rnd)
    return balls

def playGame(balls, T, timeNorm, increase, probPop):
    time = 0
    while max(balls) < T:
        oldTime = time
        index, time = drawBalls(balls, time, timeNorm)
        balls[index] += increase[index][int(random()//(1/numAttributes))]
        if floor(time) > oldTime:
            balls = popBalls(balls, probPop)
        if sum(balls) == 0 or time >= 30.0:
            return{"index":-99, "time":30, "noResolution":1}
    return{"index":balls.index(max(balls)), "time":time, "noResolution":0}

if __name__ == "__main__":
    main()