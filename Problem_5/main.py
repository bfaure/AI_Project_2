from __future__ import print_function
import os
import sys
import random
from math import sqrt
from copy import copy, deepcopy
import heapq


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




def tsp_astar(citylist):
    #boolean array of visited locations
    visited = [0]*len(citylist)
    #starting city is the first city in the file
    startCity = citylist[0]
    priorityQueue = []
    numVisited = 1
    visited[startCity.cityid] = numVisited #Mark the starting city as visited
    numVisited = numVisited + 1
    currentCity = startCity
    while(numVisited <= len(citylist)):
        for i in range(0, len(citylist)):
            #not visiting itself and city is unvisited
            if (i != currentCity.cityid  and visited[i] == 0):
                evaluation_calculation = min_distance_unvisited(currentCity, citylist, visited) + cost_calculation(currentCity, citylist[i])
                heapq.heappush(priorityQueue, (evaluation_calculation, citylist[i]))
        currentCity = heapq.heappop(priorityQueue)[1]
        while(visited[currentCity.cityid] != 0):
            currentCity = heapq.heappop(priorityQueue)[1]
        visited[currentCity.cityid] = numVisited
        numVisited = numVisited + 1
    return visited

class city(object):
    def __init__(self, city_id, x_coord, y_coord):
        self.cityid = int(city_id)
        self.x = float(x_coord)
        self.y = float(y_coord)



def main():
    #generate file here
    generateFile(10, "test.txt")
    cityList = readFile("test.txt")
    order = tsp_astar(cityList)
    print(order)


if __name__ == '__main__':
	main()
