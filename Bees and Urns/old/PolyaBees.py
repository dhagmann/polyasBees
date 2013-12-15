from random import randint, random
from joblib import Parallel, delayed
import itertools, win32api, win32process, win32con

globalBalls = (3, 3, 3, 3, 3)
globalIncrease = (2, 1, 1, 1, 1)
repetitions = 100000
outputFile = 'output.csv'

def main():
    T = [x for x in range(4,41,1)]
    probPop = [i/100 for i in range(0,21)] 
    L = list(itertools.product(T, probPop))
    results = Parallel(n_jobs=-1, verbose=50000, pre_dispatch='all')(delayed(iteration)(cross, repetitions) for cross in L)    
    
    ### Write File ###
    overview = 'startingContents,"%s"\nincreaseBy,"%s"\nIterations,%s\n\n' % (str(globalBalls), str(globalIncrease), str(repetitions))
    headers = 'probPopping,Threshold,ShareOptimal,Time\n' 
    with open(outputFile, 'w') as f: 
        f.write(overview + headers)
        f.write('\n'.join('%s,%s,%s,%s' % x for x in results)) 
    
def iteration(cross, repetitions):
    pid = win32api.GetCurrentProcessId()
    handle = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, True, pid)
    win32process.SetPriorityClass(handle, win32process.IDLE_PRIORITY_CLASS)

    T = cross[0]
    probPop = cross[1]
    count = 0
    time = 0
    for i in range(repetitions):
        balls = list(globalBalls)
        increase = list(globalIncrease)
        timeNorm = sum(balls)
        simulation = playGame(balls,T, timeNorm, increase, probPop)
        if simulation["index"] == 0:
            count +=1
        time = time+simulation["time"]
    return probPop, T, count/repetitions, time/repetitions

def drawBalls(balls, time, timeNorm):
    ''' list -> int
        Takes as input a list with balls in the urn, 
        then returns an index corresponding to the type drawn.
    '''
    rnd = randint(1, sum(balls))
    i = 0
    while sum(balls[0:i+1]) < rnd:
        i +=1
    index = i
    time = time + timeNorm/sum(balls)
    return index, time
     
def popBalls(balls):
    # This code gives equal probability
    # to popping each ball
    '''
    rndInt = randint(1, sum(balls))
    i = 0
    while sum(balls[0:i+1]) < rndInt:
        i += 1
    balls[i] = balls[i] - 1
    '''
                 
    # This code gives equal probability
    # to popping each color
    
    index = randint(0, len(balls)-1)
    while balls[index] == 0:
        index = randint(0, len(balls)-1)
    balls[index] = balls[index] - 1    
    
    return balls

def playGame(balls, T, timeNorm, increase, probPop):
    time = 0
    while max(balls) < T:
        index, time = drawBalls(balls, time, timeNorm)
        balls[index] = balls[index] + increase[index]
        if random() <= probPop:
            balls = popBalls(balls)
    return{"index":balls.index(max(balls)), "time":time}

if __name__ == "__main__":
    main()