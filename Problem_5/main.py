from __future__ import print_function
import os
import sys
import random
import time
from math import sqrt, exp
from copy import copy, deepcopy
import heapq
import re

numbers = re.compile(r'(\d+)')
def numericalSort(value):
    parts = numbers.split(value)
    parts[1::2] = map(int, parts[1::2])
    return parts

def generateAllFiles():
    num_cities_list = [10, 25, 50, 100]

    #make directory to hold files containing input data
    if not os.path.exists("data"):
        os.makedirs("data")

    for i in range(0, len(num_cities_list)):
        for j in range(0, 25):
            filename = "data/"+str(+num_cities_list[i])+"_cities_Trial_"+str(j)
            generateFile(num_cities_list[i], filename)


def generateFile(numCities, name):
    target = open(name, "w")
    target.write(str(numCities)+"\n")
    for cityId in range(0, numCities):
        x = 100 * (random.random())
        y = 100 * (random.random())
        target.write(""+str(cityId)+" "+str(x)+" "+str(y)+"\n")
    target.close()

def readFile(filename):
    target = open(filename, "r")
    text = target.read()
    lines = text.split("\n")
    cities = []
    for line in lines:
        elems = line.split(" ")
        if elems[0] != "" and elems[0] != " " and len(elems) >= 3:
            city_obj = city(elems[0], elems[1], elems[2])
            cities.append(city_obj)
    return cities

def cost_calculation(city_a, city_b):
    x_run = abs(city_a.x - city_b.x)
    y_run = abs(city_a.y - city_b.y)
    return sqrt((x_run**2)+(y_run**2))

def manhattan_heuristic(city_a, city_b):
    x_run = abs(city_a.x - city_b.x)
    y_run = abs(city_a.y - city_b.y)
    return x_run + y_run

def min_distance_unvisited(startLocation, cityList, visited):
    #calculate the manhattan distance from the start location to all others
    distance_list = []
    for city in cityList:
        if city.cityid != startLocation.cityid:
            distance_list.append((manhattan_heuristic(startLocation, city), city))
    #calculate the minimum
    minValue = sys.maxint
    foundFlag = False
    for i in range(0, len(distance_list)):
        if distance_list[i][0] < minValue and visited[distance_list[i][1].cityid] == 0:
            minValue = distance_list[i][0]
            foundFlag = True

    if foundFlag == False:
        minValue = 0

    return minValue


def total_cost_astar(citylist, order):
    tour = [None]*len(citylist)
    for i in range(0, len(order)):
        tour[order[i]-1] = citylist[i]

    return total_cost(tour)

def total_cost(tour):
    distance = 0
    for i in range(0, len(tour)):
        if i == len(tour)-1:
            distance = distance + cost_calculation(tour[i], tour[0])
        else:
            distance = distance + cost_calculation(tour[i], tour[i+1])
    return distance

def tsp_astar(citylist):
    #number of nodes generated
    nodes_generated = 0
    #boolean array of visited locations
    visited = [0]*len(citylist)
    #starting city is the first city in the file
    startCity = citylist[0]
    priorityQueue = []
    numVisited = 1
    visited[startCity.cityid] = numVisited #Mark the starting city as visited
    numVisited = numVisited + 1
    currentCity = startCity
    timeout = time.time() + 60*10 #10 minute timeout
    start = time.time()

    while(numVisited <= len(citylist) and time.time() < timeout):
        for i in range(0, len(citylist)):
            #not visiting itself and city is unvisited
            if (i != currentCity.cityid  and visited[i] == 0):
                evaluation_calculation = min_distance_unvisited(currentCity, citylist, visited) + cost_calculation(currentCity, citylist[i])
                heapq.heappush(priorityQueue, (evaluation_calculation, citylist[i]))
        currentCity = heapq.heappop(priorityQueue)[1]
        nodes_generated = nodes_generated + 1
        while(visited[currentCity.cityid] != 0):
            currentCity = heapq.heappop(priorityQueue)[1]
            nodes_generated = nodes_generated + 1
        visited[currentCity.cityid] = numVisited
        numVisited = numVisited + 1

    end = time.time()
    solved = False

    print(visited)

    if (numVisited-1) == len(citylist):
        solved = True
    execution_time = end-start
    return visited, solved, execution_time, nodes_generated

def computeProbability(currentEnergy, newEnergy, temperature):
    if newEnergy < currentEnergy:
        return 1.0
    else:
        return exp((currentEnergy - newEnergy) / temperature)

def tsp_sa(citylist):
    #set temperature
    temperature = 10000
    #set cooling rate
    coolingRate = 0.003

    #current solution
    currentTour = deepcopy(citylist)
    solved = False

    bestSolution = deepcopy(citylist)
    #number of nodes generated
    nodes_generated = 0
    timeout = time.time() + 60*10 #10 minute timeout
    start = time.time()
    while temperature > 1 and time.time() < timeout:
        #new tour
        newTour = deepcopy(currentTour)

        #Get random index positions
        position1 = random.randint(0, len(citylist)-1)
        position2 = random.randint(0, len(citylist)-1)

        #swap the cities at these positions
        temp = newTour[position1]
        newTour[position1] = newTour[position2]
        newTour[position2] = temp
        nodes_generated = nodes_generated + 1

        #get the cost for each solution
        currentCost = total_cost(currentTour)
        newCost = total_cost(newTour)

        #Decide whether to accept solution
        if computeProbability(currentCost, newCost, temperature) > random.random():
            currentTour = deepcopy(newTour)

        #Update the best solution
        if currentCost < total_cost(bestSolution):
            bestSolution = deepcopy(currentTour)

        #cool the system down
        temperature *= 1 - coolingRate
    end = time.time()
    execution_time = end-start

    if temperature < 1:
        solved = True #We've found the most optimal solution that we can get

    return bestSolution, solved, execution_time, nodes_generated


class city(object):
    def __init__(self, city_id, x_coord, y_coord):
        self.cityid = int(city_id)
        self.x = float(x_coord)
        self.y = float(y_coord)

def run_tsp_astar_trials():
    file_list = os.listdir("data/")
    #arrange the files in the order they are listed in the directory
    file_list = sorted(file_list, key=numericalSort)

    #make lists for all the data we need to gather
    solution_times_raw = []
    problems_solved_raw = []
    cost_raw = []
    nodes_generated = []
    problem_sizes = [10, 25, 50, 100]
    for f in file_list:
        cityList = readFile("data/"+f)
        visited, solved, execution_time, num_generated = tsp_astar(cityList)

        cost_raw.append(total_cost_astar(cityList, visited))
        problems_solved_raw.append(solved)
        solution_times_raw.append(execution_time)
        nodes_generated.append(num_generated)
        print("Finished trial with: "+f)

    print("Finished all trials! Writing to file...")

    #Filter out values for the solutions
    solution_times_filtered = []
    cost_filtered = []
    problems_solved = 0
    for i in range(0,100):
        if problems_solved_raw[i] == True:
            problems_solved = problems_solved + 1
            cost_filtered.append((cost_raw[i], problem_sizes[i/25], i%25))
            solution_times_filtered.append((solution_times_raw[i], problem_sizes[i/25], i%25))

    target = open("tsp_astar_results.txt", "w")
    target.write("Number of problems solved: "+str(problems_solved)+"\n")

    sum_cost = 0
    for cost in cost_filtered:
        sum_cost = sum_cost + cost[0]
    average_solution_cost = sum_cost / len(cost_filtered)
    target.write("Average solution cost (across 100 trials): "+str(average_solution_cost)+"\n")

    sum_solution_time = 0
    for sol in solution_times_filtered:
        sum_solution_time = sum_solution_time + sol[0]
    average_solution_time = sum_solution_time / len(solution_times_filtered)
    target.write("Average solution time: "+str(average_solution_time)+"\n\n")

    #Write lists to file
    target.write("Solution cost list (cost, problemsize, trial number)\n")
    target.write("----------------------------\n")
    for t in cost_filtered:
        target.write(' '.join(str(s) for s in t) + '\n')
    target.write("\n\n")

    target.write("Solution times list (time, problemsize, trial number)\n")
    target.write("----------------------------\n")
    for t in solution_times_filtered:
        target.write(' '.join(str(s) for s in t) + '\n')
    target.write("\n\n")

    target.write("Nodes generated list")
    target.write("----------------------------\n")
    for i in range(0,100):
        target.write("Size: "+str(problem_sizes[i/25])+" Trial: "+str(i%25)+" Generated: "+str(nodes_generated[i])+"\n")

    target.close()
    print("Done!")

def run_tsp_sa_trials():
    file_list = os.listdir("data/")
    #arrange the files in the order they are listed in the directory
    file_list = sorted(file_list, key=numericalSort)

    #make lists for all the data we need to gather
    solution_times_raw = []
    problems_solved_raw = []
    cost_raw = []
    nodes_generated = []
    problem_sizes = [10, 25, 50, 100]

    for f in file_list:
        cityList = readFile("data/"+f)
        tour, solved, execution_time, num_generated = tsp_sa(cityList)

        cost_raw.append(total_cost(tour))
        problems_solved_raw.append(solved)
        solution_times_raw.append(execution_time)
        nodes_generated.append(num_generated)
        print("Finished trial with: "+f)

    print("Finished all trials! Writing to file...")

    #Filter out values for the solutions
    solution_times_filtered = []
    cost_filtered = []
    problems_solved = 0
    for i in range(0,100):
        if problems_solved_raw[i] == True:
            problems_solved = problems_solved + 1
            cost_filtered.append((cost_raw[i], problem_sizes[i/25], i%25))
            solution_times_filtered.append((solution_times_raw[i], problem_sizes[i/25], i%25))

    target = open("tsp_sa_results.txt", "w")
    target.write("Number of problems solved: "+str(problems_solved)+"\n")

    sum_cost = 0
    for cost in cost_filtered:
        sum_cost = sum_cost + cost[0]
    average_solution_cost = sum_cost / len(cost_filtered)
    target.write("Average solution cost (across 100 trials): "+str(average_solution_cost)+"\n")

    sum_solution_time = 0
    for sol in solution_times_filtered:
        sum_solution_time = sum_solution_time + sol[0]
    average_solution_time = sum_solution_time / len(solution_times_filtered)
    target.write("Average solution time: "+str(average_solution_time)+"\n\n")

    #Write lists to file
    target.write("Solution cost list (cost, problemsize, trial number)\n")
    target.write("----------------------------\n")
    for t in cost_filtered:
        target.write(' '.join(str(s) for s in t) + '\n')
    target.write("\n\n")

    target.write("Solution times list (time, problemsize, trial number)\n")
    target.write("----------------------------\n")
    for t in solution_times_filtered:
        target.write(' '.join(str(s) for s in t) + '\n')
    target.write("\n\n")

    target.write("Nodes generated list")
    target.write("----------------------------\n")
    for i in range(0,100):
        target.write("Size: "+str(problem_sizes[i/25])+" Trial: "+str(i%25)+" Generated: "+str(nodes_generated[i])+"\n")

    target.close()
    print("Done!")





def main():
    #generate file here
    #generateFile(10, "test.txt")
    #cityList = readFile("test.txt")
    #order = tsp_astar(cityList)
    #print(total_cost_astar(cityList, order))
    #tsp_sa(cityList)
    #generateAllFiles()
    #run_tsp_astar_trials()

    run_tsp_sa_trials()

if __name__ == '__main__':
	main()
