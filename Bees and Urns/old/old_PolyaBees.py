import random
from time import clock

def main():
    repetitions = 10000
    for T in range(5,45,1):
        count = 0
        time = 0
        for i in range(repetitions):
            balls = [1, 1, 1, 1, 1, 1]
            increase = [2, 1, 1, 1, 1, 1]
            timeNorm = sum(balls)
            simulation = playGame(balls,increase,T, timeNorm)
            if simulation["index"] == 0:
                count +=1
            time = time+simulation["time"]
        print("Threshold: " + str(T) +"\t Share Correct: " + str(count/repetitions) +"\t Time: " + str(time/repetitions))

def drawBalls(balls, time, timeNorm):
    ''' list -> int
        Takes as input a list with balls in the urn, 
        then returns an index corresponding to the type drawn.
    '''
    rnd = random.randint(1, sum(balls))
    i = 0
    while sum(balls[0:i+1]) < rnd:
        i +=1
    time = time + timeNorm/sum(balls)
    return {"index":i, "time":time}

def addBalls(balls,increase, index):
    ''' list -> list
        Takes as input the balls in the urn and the rate at
        which each type should be increased, if drawn.
        Returns updated balls in the urn after draw.
    '''
    balls[index] = balls[index] + increase[index]
    return balls

def playGame(balls, increase, T, timeNorm):
    time = 0
    while max(balls) < T:
        draw = drawBalls(balls, time, timeNorm)
        index = draw["index"]
        time = draw["time"]
        balls = addBalls(balls, increase, index)
    return{"index":balls.index(max(balls)), "time":time}

if __name__ == "__main__":
    start = clock()
    main()
    print(clock()-start)