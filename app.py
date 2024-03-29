import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import random
import pandas as pd

# City class
class City:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    # Calculate distance between two cities
    def distance(self, city):
        xDis = abs(self.x - city.x)
        yDis = abs(self.y - city.y)
        distance = np.sqrt((xDis ** 2) + (yDis ** 2))
        return distance

    def __repr__(self):
        return "(" + str(self.x) + "," + str(self.y) + ")"

# Fitness class
class Fitness:
    def __init__(self, route):
        self.route = route
        self.distance = 0
        self.fitness = 0.0

    # Calculate total distance of the route
    def routeDistance(self):
        if self.distance == 0:
            pathDistance = 0
            for i in range(0, len(self.route)):
                fromCity = self.route[i]
                toCity = None
                if i + 1 < len(self.route):
                    toCity = self.route[i + 1]
                else:
                    toCity = self.route[0]
                pathDistance += fromCity.distance(toCity)
            self.distance = pathDistance
        return self.distance

    # Calculate fitness of the route
    def routeFitness(self):
        if self.fitness == 0:
            self.fitness = 1 / float(self.routeDistance())
        return self.fitness

# Create random routes for the initial population
def createRoute(cityList):
    route = random.sample(cityList, len(cityList))
    return route

# Create the initial population
def initialPopulation(popSize, cityList):
    population = []
    for i in range(0, popSize):
        population.append(createRoute(cityList))
    return population

# Rank individuals
def rankRoutes(population):
    fitnessResults = {}
    for i in range(0, len(population)):
        fitnessResults[i] = Fitness(population[i]).routeFitness()
    return sorted(fitnessResults.items(), key=lambda x: x[1], reverse=True)

# Create a selection function that will be used to make the list of parent routes
def selection(popRanked, eliteSize):
    selectionResults = []
    df = pd.DataFrame(np.array(popRanked), columns=["Index", "Fitness"])
    df["cum_sum"] = df.Fitness.cumsum()
    df["cum_perc"] = 100 * df.cum_sum / df.Fitness.sum()
    for i in range(0, eliteSize):
        selectionResults.append(popRanked[i][0])
    for i in range(0, len(popRanked) - eliteSize):
        pick = 100 * random.random()
        for i in range(0, len(popRanked)):
            if pick <= df.iat[i, 3]:
                selectionResults.append(popRanked[i][0])
                break
    return selectionResults

# Create mating pool
def matingPool(population, selectionResults):
    matingpool = []
    for i in range(0, len(selectionResults)):
        index = selectionResults[i]
        matingpool.append(population[index])
    return matingpool

# Create a crossover function for two parents to create one child
def breed(parent1, parent2):
    child = []
    childP1 = []
    childP2 = []
    geneA = int(random.random() * len(parent1))
    geneB = int(random.random() * len(parent1))
    startGene = min(geneA, geneB)
    endGene = max(geneA, geneB)
    for i in range(startGene, endGene):
        childP1.append(parent1[i])
    childP2 = [item for item in parent2 if item not in childP1]
    child = childP1 + childP2
    return child

# Create function to run crossover over full mating pool
def breedPopulation(matingpool, eliteSize):
    children = []
    length = len(matingpool) - eliteSize
    pool = random.sample(matingpool, len(matingpool))
    for i in range(0, eliteSize):
        children.append(matingpool[i])
    for i in range(0, length):
        child = breed(pool[i], pool[len(matingpool) - i - 1])
        children.append(child)
    return children

# Create function to mutate a single route
def mutate(individual, mutationRate):
    for swapped in range(len(individual)):
        if random.random() < mutationRate:
            swapWith = int(random.random() * len(individual))
            city1 = individual[swapped]
            city2 = individual[swapWith]
            individual[swapped] = city2
            individual[swapWith] = city1
    return individual

# Create function to run mutation over entire population
def mutatePopulation(population, mutationRate):
    mutatedPop = []
    for ind in range(0, len(population)):
        mutatedInd = mutate(population[ind], mutationRate)
        mutatedPop.append(mutatedInd)
    return mutatedPop

# Create function to produce next generation
def nextGeneration(currentGen, eliteSize, mutationRate):
    popRanked = rankRoutes(currentGen)
    selectionResults = selection(popRanked, eliteSize)
    matingpool = matingPool(currentGen, selectionResults)
    children = breedPopulation(matingpool, eliteSize)
    nextGeneration = mutatePopulation(children, mutationRate)
    return nextGeneration

# Final step: create the genetic algorithm
def geneticAlgorithm(population, popSize, eliteSize, mutationRate, generations):
    pop = initialPopulation(popSize, population)

    # Print all routes as a single array of routes
    all_routes = []
    for route in pop:
        all_routes.append(route)
    st.write("All Routes:")
    st.write(all_routes)

    st.write("Initial distance: " + str(1 / rankRoutes(pop)[0][1]))

    for i in range(0, generations):
        pop = nextGeneration(pop, eliteSize, mutationRate)

    st.write("Final distance: " + str(1 / rankRoutes(pop)[0][1]))

    bestRouteIndex = rankRoutes(pop)[0][0]
    bestRoute = pop[bestRouteIndex]

    # Print the best route
    st.write("Best Route:")
    st.write(bestRoute)

    return bestRoute


def main():
    st.title("TSP GA Solver")

    run_button = st.button("Run Genetic Algorithm")

    if run_button:
        run_genetic_algorithm()

def run_genetic_algorithm():
    # Define global variables
    POPULATION_SIZE = 100
    ELITE_SIZE = 20
    MUTATION_RATE = 0.01
    NUMBER_OF_GENERATIONS = 500

    # Create list of cities
    cityList = []

    for i in range(0, 25):
        cityList.append(City(x=int(random.random() * 200), y=int(random.random() * 200)))

    # Run the genetic algorithm
    bestRoute = geneticAlgorithm(population=cityList, popSize=POPULATION_SIZE, eliteSize=ELITE_SIZE,
                                 mutationRate=MUTATION_RATE, generations=NUMBER_OF_GENERATIONS)
    # Plot the best route
    fig, ax = plt.subplots()
    ax.plot([city.x for city in bestRoute], [city.y for city in bestRoute], 'b-')
    ax.plot([cityList[0].x, cityList[0].x], [cityList[0].y, cityList[0].y], 'ro')
    ax.set_title('Best Route')
    st.pyplot(fig)

    # Plot the best route
    # plt.plot([city.x for city in bestRoute], [city.y for city in bestRoute], 'b-')
    # plt.plot([cityList[0].x, cityList[0].x], [cityList[0].y, cityList[0].y], 'ro')
    # plt.title('Best Route')
    # st.pyplot()

if __name__ == "__main__":
    main()
