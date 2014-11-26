#!/usr/bin/env python
# Tests the classes in .../classes/Environment.py

import sys
import os
import copy
import random
import itertools

locationOfFiles = os.getcwd() + '/classes'  # add location of class files to PYTHONPATH
print 'File loc: ', locationOfFiles
sys.path.append(locationOfFiles)

from environment import Location, Bounds2D, World
from neuralNet import *

def initNNs(lenOfPool, numAgents):
    ''' Creates a pool of neuralNets 
        Each sublist corresponds to an agent's pool of NNs, so its length is the number of nn in a pool
        Length of the list is the number of agents.

        @author Kory Kraft
    '''
    nnList = []
    for agent in range(numAgents):
        agentsNNList = []
        for i in range(lenOfPool):
            agentsNNList.append(createNN())
        nnList.append(agentsNNList)
    return nnList


def createNN():
    ''' Creates a 1 hidden layer ff-nn of input 8, hidden layer 10, and output 2 
    @author Kory Kraft
    '''
    nn = NeuralNetwork(8, 10, 2)
    nn.createNodes()
    nn.createRandomWeights()
    return nn

def createTeams(nns):
    ''' 
    Creates a 'team' of agents.  Can be thought of as creating a team of agents' brains.
    In reality, it selects a previously unselected NN from each agent's NN pool.
    
    @author Kory Kraft  
    '''
    allTeams = [] # list that will hold each team of agents' nns

    # Shuffle each sublist of agent's nns
    for agentNNs in nns:
        random.shuffle(agentNNs)

    # create k teams
    #   where the nn from each agent is "picked" from the shuffled list
    for k in range(lenOfPool):
        team = []
        for agentNNs in nns:
            team.append(agentNNs[k])
        allTeams.append(team)

    # Works but slow and could looop for a loooooong time
    # for agentPool in nns:
    #     print agentPool
    #     i = 0 
    #     while True:
    #         i += 1
    #         if i == 100:
    #             print 'hit 100'
    #             sys.exit(1)

    #         agentNN = random.choice(agentPool)
    #         print 'Selected ', agentNN.selected
    #         if agentNN.selected == False:
    #             agentNN.selected = True
    #             team.append(agentNN)
    #             break

    #  Wrong!!!


    # Create randomized selection indices for each agent's nn to create the random teams
    # It is a list of lists.  Each sublist corresponds to the selection indices for the nn
    # agentSelChoices = [] # selection indices for the nn for each agent
    # for agent in range(numAgents):
    #     indices = [x for x in range(lenOfPool)]
    #     random.shuffle(indices)
    #     agentSelChoices.append(indices) 
    # allTeams = [] # will hold a list of nns
    #             # indices of the list correspond to agents.  E.g. list[1] is agent 1's nn
    # for teamSel in teamSelChoices:
    #     print 'Team sel: ', teamSel
    #     team = []
    #     for selection, agentsNN in itertools.izip(teamSel, nns):
    #         print 'Selection: ', selection
    #         team.append(agentsNN[selection])
    #     allTeams.append(team)

    # print 'Number of team members ', len(allTeams[0])
    # print 'Number of teams ', len(allTeams)
    return allTeams

def updateNNS(nns, egreedy):
    ''' Selects the top performers of nns for each agent
        Mutates these and replaces the lower performers.

        Note: Keeps the same neural networks in memory, but with different weights.
    '''

    for agentNNs in nns:        
        # Divide out the agent's nns in the the high performers and low performers
        topHalfNNs, lowHalfNNs = selectPerformers(agentNNs, egreedy)
        # mutate the top performers and replace the lowHalfNN's with these mutate weights
        mutateNNs(topHalfNNs, lowHalfNNs)


def selectPerformers(nns, egreedy):
    ''' Given a list a nueral networks,
         this method selects the top half performers, 
         always keeping the highest performer,
         and e-greedy times switching other low-high performers

         Returns: List of nns that were the top performers
    @ author Kory Kraft
    '''
    # sort the agent's nns according to value from low to high
    sorted(nns, key=lambda nn: nn.value)

    # keep the highest, and e-greedy time swap out a low performer with a high performer
    # get the top half of the list (those are the highest performers)
    midPointIndex = int(len(nns)/2)
    topHalf = nns[midPointIndex:] 
    lowHalf = nns[:midPointIndex]
    
    # take egreedy high performers (minus the highest), and swap out with the lower half
    for i in xrange(int(len(nns) * egreedy)):
        # randomly insert switch one high performer with low performer (don't want to just assign low performer to high otherwise we might get weird linking errors)
        index = random.randint(0,midPointIndex-2) # <- prevent from indexing out of bounds and ensures that highest one is excluded (i.e. kept in top half)
        temp = lowHalf[index]
        lowHalf[index] = topHalf[index]
        topHalf[index] = temp

    return topHalf, lowHalf


def mutateNNs(topHalf, lowHalf):
    ''' Each nn in the low half is replaced by a mutated version of the nn in the topHalf. 
        Leaves the low nn in the same memory address (for the sake of the larger nns matrix.
        Instead, does a deep copy of the weights in the mutated nn.

        @author: Kory Kraft
        '''

    for low, top in zip(lowHalf, topHalf):
        low.weights = top.mutateWeights(.1).weights
        low.value = sys.float_info.min

def calcDX(output, maxDist, noise):
    ''' Calculates dx taking into account the noise.
        The actual noise rate is taking from a uniform distribution between
            +- noise.

        dx = 2maxD(x - .5) * noise ; this came from Tumer's paper
    @author Kory Kraft
    '''
    dx = 2 * maxDist * (x - .5)
    noiseDist = random.uniform(-noise, noise) * dx
    dx = dx + noiseDist
    return dx


def doEpisode(world, team, timesteps, maxDist, minDist, mvtNoise, headings):
    # reset world
    # init/place rovs
    world.reset(headings)  # randomize POI locations and reset rover locations
    for t in range(timesteps):
        for rov, nn in itertools.izip(world.rovers, team):
            # Do a prediction with the rovs associated nn from the team
            x,y = nn.fasterPredict(rov.getNNInputs(world.POIs, minDist, world.rovers)) 
            dy = calcDX(y, maxDist, mvtNoise)
            
            # take the action with the pred. action
            rov.takeAction(dx, dy)
            
    # Get rewards for nn's which correspond to system rewards   
    rewards, rover_closest_list = world.get_rewards()
    for nn, reward in itertools.izip(team, rewards['DIFFERENCE']):
        nn.value = reward
    pass

def main():
    # Evo Training
    # 
    # Until convergence
    #     For num of NNs each agent has (length of the pool)
    #        Create team ( selected previously unselected NN from each row)
    #        Do an episode (do stuff in world for 15 time steps and get rewards)
    #        Assign each individual NN in the current team a value based on the 
    #          corresponding agent performance/rewards
    #     Select top NN performers from each agent's NN pool e-greey, but keep top 1 each time
    #     Mutate the above
    #     Replace the unselected onces 

    # Hyperparamters for training
    lenOfPool = 10 # Num of nn's for each agent 
    numAgents = 5 # Num of agents in the system
    timesteps = 15
    maxDist = 10 # maximum distance the agent can move in one timestep
    minDist = 5 # minimum distance 
    mvtNoise = .1 # the noise added to each actions outcome
    nns = initNNs(lenOfPool, numAgents) # Can be thought of as matrix of NNs, each sublist is an agents pool of nns
    # random headings for agent that will stay 
    # the same for each agent through the runs and epochs
    #  so that the corresponding agent and nn pool will reflect the 
    #   same initial values/assumptions
    agentInitHeadings = [(random.randint(0,359) * math.pi /180) for x in range(numAgents)] 
    egreedy = .2 # number of weights to mutate starting out, this is decreased over time 
    egreedyDecreaseRate = .9 # rate at which egreedy selection is decreased

    # World parameters
    world_bounds = Bounds2D((0, 115), (0, 100))  # world borders
    world_center = Location(60, 50)  # where the agents start at
    poi_ranges = (70, 70)
    poi_bounds = Bounds2D((world_center.x-poi_ranges[0]/2, world_center.x+poi_ranges[0]/2), 
                          (world_center.y-poi_ranges[1]/2, world_center.y+poi_ranges[1]/2))  # bounds of where POIs can go

    world = World(world_bounds, 100, poi_bounds, 30, rover_start=world_center, rovHeadings=agentInitHeadings)  # make a world

    # Create orientations for the agents outside so they will all be consist for agent i
    for i in range(3): # random definition of convergence

        # create random team of agent brains for the game
        teams = createTeams(nns)

        for team in teams:         
            # do the episode
            doEpisode(world, team, timesteps, maxDist, minDist, mvtNoise)
        
        # select best nn performers
        #   and mutate and replace low performers
        updateNNS(nns, egreedy * egreedyDecreaseRate)


if __name__ == "__main__":
    main()
    
