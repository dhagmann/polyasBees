from random import random, randint, uniform
from joblib import Parallel, delayed
import itertools, win32api, win32process, win32con
import csv, time
import lockfile

repetitions = 100000
simType = "numTypes"

if simType == "numTypes":
    globalBalls = ((1, 1), (1, 1, 1), (1, 1, 1, 1))
    globalIncrease = (((2,),(1,), (1,), (1,)),)
    disruptionRate = [0,]
    discoveryRate = [0,]
    discoveryRateOptimal = [0,]
    recruitmentRate = [1,]
if simType == "ratios":
    globalBalls = ((1, 1, 1),)
    globalIncrease = (((3,),(1,), (1,)), ((3,),(2,), (1,)))
    disruptionRate = [0,]
    discoveryRate = [0,]
    discoveryRateOptimal = [0,]
    recruitmentRate = [1,]
if simType == "noise":
    globalBalls = ((1, 1),)
    globalIncrease = (((3, 2, 2, 1),(2, 1, 1, 0)), ((2, 2, 2, 2),(1, 1, 1, 1)))
    disruptionRate = [0,]
    discoveryRate = [0,]
    discoveryRateOptimal = [0,]
    recruitmentRate = [1,]
if simType == "multiAttributesFixed":
    globalBalls = ((1, 1),)
    globalIncrease = (((3, 1), (1, 1)),((2, 2), (1, 1)))
    disruptionRate = [0,]
    discoveryRate = [0,]
    discoveryRateOptimal = [0,]
    recruitmentRate = [1,]
if simType == "multiAttributesDirectComparison":
    globalBalls = ((1, 1),)
    globalIncrease = (((3, 1), (2, 2)),)
    disruptionRate = [0,]
    discoveryRate = [0,]
    discoveryRateOptimal = [0,]
    recruitmentRate = [1,]
if simType == "infoCascade":
    globalBalls = ((1, 3),)
    globalIncrease = (((2,), (1,)),)
    disruptionRate = [0, 0.05, 0.10, 0.20]
    discoveryRate = [0,]
    discoveryRateOptimal = [0,]
    recruitmentRate = [1,]
if simType == "varyingSuboptimalPayoff":
    globalBalls = ((1, 1),)
    globalIncrease = (((4,), (1,)), ((4,), (2,)), ((4,), (3,)))
    disruptionRate = [0,]
    discoveryRate = [0,]
    discoveryRateOptimal = [0,]
    recruitmentRate = [1,]
if simType == "varyingOptimalPayoff":
    globalBalls = ((1, 1),)
    globalIncrease = (((2,), (1,)), ((3,), (1,)), ((4,), (1,)))
    disruptionRate = [0,]
    discoveryRate = [0,]
    discoveryRateOptimal = [0,]
    recruitmentRate = [1,]
if simType == "discovery":
    globalBalls = ((0, 0),)
    globalIncrease = (((2,),(1,),),)
    disruptionRate = [0.5]
    discoveryRate = [0.25,0.75]
    discoveryRateOptimal = [0.1,0.75]
    recruitmentRate = [0.5,]

outputFile = simType + "February2014.csv"

numAttributes = len(globalIncrease[0][0])
def main():
    with open(outputFile, 'w') as f: 
        headers = 'disruptionRateping,threshold,numChoices,option1,option2,time,noResolution,startingContents,increaseRates,discoveryRate,discoveryRateOptimal,recruitmentRate\n' 
        f.write(headers)
                
    T = [x for x in range(1,100,1)]
    L = list(itertools.product(disruptionRate, T, globalBalls, globalIncrease, discoveryRate, discoveryRateOptimal, recruitmentRate))
    Parallel(n_jobs=-1, verbose=500000, pre_dispatch='all')(delayed(iteration)(cross, repetitions) for cross in L)

def iteration(cross, repetitions):
    pid = win32api.GetCurrentProcessId()
    handle = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, True, pid)
    win32process.SetPriorityClass(handle, win32process.IDLE_PRIORITY_CLASS)
    disruptionRate, T, iterationBalls, iterationIncrease, discoveryRate, discoveryRateOptimal, recruitmentRate = cross
    output = []
    for i in range(repetitions):
        # Set up new iteration
        balls = list(iterationBalls)
        increase = list(iterationIncrease)
        numTargets = len(balls)
        # Run iteration
        simulation = playGame(balls,T, increase, disruptionRate, discoveryRate, discoveryRateOptimal, recruitmentRate)
        # Record Results
        if simulation["index"] == 0:
            option1 = 1
            option2 = 0
        elif simulation["index"] == 1:
            option1 = 0
            option2 = 1
        else:
            option1, option2 = 0,0
        time = simulation["time"]
        if simulation["noResolution"] == 1:
            option1 = 0
            option2 = 0
            time = 0
        noResolution = simulation["noResolution"]
        output.append([disruptionRate, T, numTargets, option1, option2, time, noResolution, iterationBalls, iterationIncrease, discoveryRate, discoveryRateOptimal, recruitmentRate])
    writeToFile(output)
    
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

def playGame(balls, T, increase, disruptionRate, discoveryRate, discoveryRateOptimal, recruitmentRate):
    time = 0
    count = 0
    if discoveryRate == 0 and sum(balls) == 0:
        return{"index":-88, "time":0, "noResolution":1}
    while max(balls) < T:
        chooseAction = uniform(0, discoveryRate + sum(balls)*(disruptionRate + recruitmentRate))
        if chooseAction <= discoveryRate:
            if uniform(0,1) <= discoveryRateOptimal:
                balls[0] += 1
            else:
                balls[1] += 1         
        elif chooseAction <= discoveryRate + sum(balls)*(disruptionRate):
            if sum(balls) != 0:
                balls = popBalls(balls)
        elif chooseAction <= discoveryRate + sum(balls)*(disruptionRate + recruitmentRate):
            if sum(balls) != 0:
                balls = drawBalls(balls, increase)
        time += incrementTime(balls, discoveryRate, recruitmentRate, disruptionRate)
        count += 1
        if count >= 20000:
            return{"index":-99, "time":0, "noResolution":1}
    return{"index":balls.index(max(balls)), "time":time, "noResolution":0}

def incrementTime(balls, discoveryRate, recruitmentRate, disruptionRate):
    increment = 1/(sum(balls)*(recruitmentRate + disruptionRate) + discoveryRate)
    return increment

def writeToFile(data):
    lock = lockfile.FileLock(outputFile)
    lock.acquire()
    with open(outputFile, 'a') as f:  
        save = csv.writer(f, lineterminator='\n')
        save.writerows(data)
    lock.release()

if __name__ == "__main__":
    main()