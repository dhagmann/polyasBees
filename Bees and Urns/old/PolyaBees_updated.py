from random import random, randint
from math import floor
from joblib import Parallel, delayed
import itertools, win32api, win32process, win32con

globalBalls = (1, 1, 1)
globalIncrease = (2, 1, 1)
repetitions = 20000
outputFile = '2013-05-15_multiAttributes_noiseControl.csv'

def main():
    T = [x for x in range(5,25,1)] + [y for y in range(25,80,5)] + [z for z in range(80,301,10)]
    probPop = [i/100 for i in range(0,21,5)]
    L = list(itertools.product(T, probPop))
    results = Parallel(n_jobs=-1, verbose=50000, pre_dispatch='all')(delayed(iteration)(cross, repetitions) for cross in L)    
    
    ### Write File ###
    overview = 'startingContents,"%s"\nincreaseBy,"%s"\nIterations,%s\n\n' % (str(globalBalls), str(globalIncrease), str(repetitions))
    headers = 'probPopping,Threshold,ShareOptimal,Time,NoResolution\n' 
    with open(outputFile, 'w') as f: 
        f.write(overview + headers)
        f.write('\n'.join('%s,%s,%s,%s,%s' % x for x in results)) 
    
def iteration(cross, repetitions):
    pid = win32api.GetCurrentProcessId()
    handle = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, True, pid)
    win32process.SetPriorityClass(handle, win32process.IDLE_PRIORITY_CLASS)

    T, probPop = cross
    count, time, noResolution = 0, 0, 0

    for i in range(repetitions):
        balls = list(globalBalls)
        increase = list(globalIncrease)
        timeNorm = sum(balls)
        simulation = playGame(balls,T, timeNorm, increase, probPop)
        if simulation["index"] == 0:
            count +=1
        time = time+simulation["time"]
        noResolution += simulation["noResolution"]
        if repetitions == noResolution:
            avgTime = 0
        else:
            avgTime = time/(repetitions - noResolution)
    return probPop, T, count/repetitions, avgTime, noResolution

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
        balls[index] += increase[index]
        if floor(time) > oldTime:
            balls = popBalls(balls, probPop)
        if sum(balls) == 0 or time >= 25.0:
            return{"index":1, "time":0, "noResolution":1}
    return{"index":balls.index(max(balls)), "time":time, "noResolution":0}

if __name__ == "__main__":
    main()
    # cProfile.run('iteration([30,0.10], 10000)')