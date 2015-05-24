__author__ = 'Romain'


from geopy.geocoders import Nominatim
from geopy.distance import vincenty
from geopy.exc import GeocoderTimedOut
from itertools import combinations
import random


geolocator = Nominatim()
# WPointsCoord = []  # list which will hold the list of the waypoints' coordinates
WPointName = []
# startDist = []
# endDist = []
# WPointDist = []
# WPointRoute = []
cityLat = {}
cityLong = {}

print("Enter the name of the city you want to start from.")
startPoint = input()
sLoc = geolocator.geocode(startPoint)
cityLat[startPoint] = sLoc.latitude
cityLong[startPoint] = sLoc.longitude

print("Enter your final destination.")
endPoint = input()
eLoc = geolocator.geocode(endPoint)
cityLat[endPoint] = eLoc.latitude
cityLong[endPoint] = eLoc.longitude

print("Enter number of way points desired (Final destination not included).")
numb = int(input())
for x in range(numb):
    print("Enter waypoint number ", x+1)
    pX = input()
    pXLoc = geolocator.geocode(pX)
    WPointName.append(pX)

    cityLat[pX] = pXLoc.latitude
    cityLong[pX] = pXLoc.longitude
    # pXCoord = [pXLoc.latitude, pXLoc.longitude]  # list of the coordinates, one is created for each waypoint
    # WPointsCoord.append(pXCoord)
    #
    # distFromStart = vincenty(sCoord, pXCoord).kilometers
    # distToEnd = vincenty(pXCoord, eCoord).kilometers
    # startDist.append(distFromStart)
    # endDist.append(distToEnd)

# Populate the array of distances between the cities
# for (WPoint1, WPoint2) in combinations(WPointsCoord, 2):
#     dist = vincenty(WPoint1, WPoint2).kilometers
#     dist = round(dist, 2)
#     WPointDist.append(dist)

# Populate the array with the names of the routes to match the distances
# for(WPoint1, WPoint2) in combinations(WPointName, 2):
#     rName = (WPoint1, "and", WPoint2)
#     WPointRoute.append(rName)

# Checks that the size of the lists are the same as they should be, and prints the distances between
# cities in a nicer way
# if len(WPointDist) == len(WPointRoute):
#     for x in range(len(WPointDist)):
#         print("The distance between ", WPointRoute[x], "is ", WPointDist[x], "kilometers")

# print(cityLat)
# print(cityLong)
def create_random_route():
    # initialise the random route with the starting point
    random_route = []
    random_route.append(startPoint)

    # shuffles the list of the waypoints. If that is not done, then the list created will always be the same
    random.shuffle(WPointName)

    # add all the desired waypoints to that list
    for i in range(len(WPointName)):
        random_route.append(WPointName[i])

    # add the destination of the travel
    random_route.append(endPoint)

    return tuple(random_route)


# Create the pool of routes which is needed to start choosing the best ones
def create_list_routes(list_size):
    list_routes = []
    for route in range(list_size):
        list_routes.append(create_random_route())
    return list_routes


# This is the fitness function. In this case, the smaller the total distance, the fitter the route
def calculate_total_distance(route):
    t_distance = 0.0
    # route_1 = list(route)

    for j in range(len(route)-1):
        # get the waypoints
        w1 = route[j - 1]
        # print(w1)
        w1_lat = 0
        w1_long = 0
        # w1_loc = geolocator.geocode(w1)
        w2 = route[j]
        w2_lat = 0
        w2_long = 0
        # w2_loc = geolocator.geocode(w2)
        if w1 in cityLat:
            w1_lat = cityLat[w1]
            # print("Found cities!")
        if w1 in cityLong:
            w1_long = cityLong[w1]
        if w2 in cityLat:
            w2_lat = cityLat[w2]
        if w2 in cityLong:
            w2_long = cityLong[w2]
        # get their coordinates
        w1_coord = [w1_lat, w1_long]
        w2_coord = [w2_lat, w2_long]

        # add their distance to the total distance of the route
        t_distance += vincenty(w1_coord, w2_coord).kilometers

    # print(t_distance)
    return t_distance


# Then have a method which will mutate the route it is passed
# This changes the place of items to another random one; if two items are at the same place, continue changing it until
# it is not the case anymore
def genetic_mutation(route, times):
    mutate_list = list(route)
    # print(route)
    for swap_items in range(times):
        index1 = random.randint(1, len(mutate_list) - 2)
        index2 = index1

        while index2 == index1:
            index2 = random.randint(1, len(mutate_list) - 2)

        mutate_list[index1], mutate_list[index2] = mutate_list[index2], mutate_list[index1]

    return tuple(mutate_list)


# And have a function which will randomly change the route around (smaller occurrence then genetic mutation)
# This random mutation will take the first half of the waypoints and exchange their place with the second half
def random_route_mutation(route):
    route_mutate = list(route)

    if(len(route_mutate) % 2) == 0:
        first_half = route_mutate[:int((len(route_mutate)/2))]
        second_half = route_mutate[int((len(route_mutate)/2)):]
        route_mutate = second_half + first_half
    else:
        n1 = int((len(route_mutate) - 1) / 2)
        n2 = int((len(route_mutate) + 1) / 2)
        first_half = route_mutate[:n1]
        second_half = route_mutate[n2:]
        route_mutate = second_half + first_half

    return tuple(route_mutate)


# In the main genetic method, only the routes which have the smallest total distance will be selected for mutation
def main_function(mutation_times, number_routes):
    # create the pool of routes, make it so the size of the pool depends on the number of inputs given by the user
    route_list = create_list_routes(number_routes)
    # print(route_list)
    # loop through the number of mutations given by mutation_times
    for times_loop in range(mutation_times):
        # apply the fitness function to each of the pool routes
        route_fitness = {}

        # loop through the list of routes and store each route's fitness
        for route in route_list:
            # checks if the route's fitness has already been calculated
            if route in route_fitness:
                continue
            route_fitness[route] = calculate_total_distance(route)

        # create the new list of routes which will be populated of the next, fitter generation
        new_route_list = []

        # create the value which will be the top 10% of the route, do rounding up for non ints
        best_10_percent = int(0.1 * number_routes)
        if best_10_percent < 1:
            best_10_percent = 1

        # chance_random_mutation = 0.3
        # mutate the 10 best of each generation of routes
        for (pos, best_route) in enumerate(sorted(route_fitness, key=route_fitness.get)[:best_10_percent]):
            if pos == 0:
                print("The best route is", best_route, "with a total distance of ", route_fitness[best_route])
            # put the best route in the new list
            new_route_list.append(best_route)
            # print(best_route)
            # populate the rest of the list with mutated routes
            for mutated_route in range(number_routes - best_10_percent - 2):
                new_route_list.append(genetic_mutation(best_route, 2))
                # print(best_route)
            # random mutation, one per mutation
            random_route_mutation(best_route)
            new_route_list.append(best_route)
            # print(best_route)

        # delete the contents of the list to be replaced by the new one
        for t in range(len(route_list))[::-1]:
            del route_list[t]

        # print(route_list)
        route_list = new_route_list

main_function(1000, 100)

