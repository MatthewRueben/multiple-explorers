#!/usr/bin/env python
# Tests the classes in .../classes/Environment.py

import sys
import os
import copy
import random
import itertools
import timeit
#from matplotlib import pyplot

locationOfFiles = os.getcwd() + '/classes'  # add location of class files to PYTHONPATH
print 'File loc: ', locationOfFiles
sys.path.append(locationOfFiles)

from environment import Location, Bounds2D, World
from roverSettingsStruct import RoverSettings
from neuralNet import *

def initNNs(lenOfPool, numAgents):
    ''' Creates a pool of neuralNets 
        Each sublist corresponds to an agent's pool of NNs, so its length is the number of nn in a pool
        Length of the list is the number of agents.

        @author Kory Kraft
    '''
    # Ask Dr. Smart about this section.  Have to deep copy both the list and the nn.
    # Cannot even just createNN() inside the append.
    # Whats up?
    # Kory Kraft 11/26/2014 
    # nnList = []
    # for agent in range(numAgents):
    #     agentsNNList = []
    #     for i in range(lenOfPool):
    #         agentsNNList.append(createNN())
    #     nnList.append(agentsNNList)
    # return nnList

    nnList = []
    for agent in range(numAgents):
        agentsNNList = []
        for i in range(lenOfPool):
            nn = createNN()
            agentsNNList.append(copy.deepcopy(nn))
        nnList.append(copy.deepcopy(agentsNNList) )
    return nnList


def createNN():
    ''' Creates a 1 hidden layer ff-nn of input 8, hidden layer 10, and output 2 
    @author Kory Kraft
    '''
    nn = NeuralNetwork(8, 10, 2)
    nn.createNodes()
    nn.createRandomWeights()
    return nn

def createTeams(nns, lenOfPool):
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
    sortedNNS = sorted(nns, key=lambda nn: nn.value)

    # keep the highest, and e-greedy time swap out a low performer with a high performer
    # get the top half of the list (those are the highest performers)
    midPointIndex = int(len(sortedNNS)/2)
    topHalf = sortedNNS[midPointIndex:] 
    lowHalf = sortedNNS[:midPointIndex]
    
    # take egreedy high performers (minus the highest), and swap out with the lower half
    for i in xrange(int(len(sortedNNS) * egreedy)):
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
    dx = 2 * maxDist * (output - .5)
    noiseDist = random.uniform(-noise, noise) * dx
    dx = dx + noiseDist
    return dx


def doEpisode(world, team, timesteps, maxDist, minDist, mvtNoise, headings, rewardType, moveRandomly=False):

    # reset world
    # init/place rovs
    world.reset(headings)  # randomize POI locations and reset rover locations
    for t in range(timesteps):
        for rov, nn in itertools.izip(world.rovers, team):
            # Do a prediction with the rovs associated nn from the team
            o1, o2 = nn.fasterPredict(rov.getNNInputs(world.POIs, minDist, world.rovers)) 
            if moveRandomly:
                dx = random.uniform(-maxDist, maxDist)  # pick random actions
                dy = random.uniform(-maxDist, maxDist)
            else:
                dx = calcDX(o1, maxDist, mvtNoise)  # use the neural network's actions
                dy = calcDX(o2, maxDist, mvtNoise)
            
            # take the action with the chosen action
            rov.takeAction(dx, dy)
            
    # Get rewards for nn's which correspond to system rewards   
    rewards, rover_closest_list = world.get_rewards()  # get all the different reward types
    rewards_chosen = rewards[rewardType]  # pick the reward type
    if rewardType == 'GLOBAL':  # the global reward is length 1 and needs to be tiled
        rewards_chosen = [rewards_chosen]*len(team)  
    for nn, reward in itertools.izip(team, rewards_chosen):  # assign rewards to NN's
        nn.value = reward

    return rewards['GLOBAL']

def main(roverSettings = RoverSettings(), episodes = 200, lengthOfPool = 40):
    ''' Returns reward list for the system at each episode. '''
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

    # Gridworld Domain variables 
    rewardType = roverSettings.rewardType
    lenOfPool = lengthOfPool # Num of nn's for each agent 
    numAgents = roverSettings.numAgents # Num of agents in the system
    moveRandomly = roverSettings.moveRandomly
    numPoi = 100
    timesteps = 15
    maxDist = 10 # maximum distance the agent can move in one timestep
    minDist = 5 # minimum distance 
    mvtNoise = .1 # the noise added to each actions outcome

    # matrix of nns for each agent in system 
    nns = initNNs(lenOfPool, numAgents) # Can be thought of as matrix of NNs, each sublist is an agents pool of nns
    # random headings for agent that will stay 
    # the same for each agent through the runs and epochs
    #  so that the corresponding agent and nn pool will reflect the 
    #   same initial values/assumptions
    agentInitHeadings = [(random.randint(0,359) * math.pi /180) for x in range(numAgents)] 
    
    # Hyperparamters for training
    egreedy = .2 # number of weights to mutate starting out, this is decreased over time 
    egreedyDecreaseRate = .9 # rate at which egreedy selection is decreased

    # World parameters
    world_bounds = Bounds2D((0, 115), (0, 100))  # world borders
    world_center = Location(60, 50)  # where the agents start at
    poi_ranges = (70, 70)
    poi_bounds = Bounds2D((world_center.x-poi_ranges[0]/2, world_center.x+poi_ranges[0]/2), 
                          (world_center.y-poi_ranges[1]/2, world_center.y+poi_ranges[1]/2))  # bounds of where POIs can go

    
    # self, world_bounds, N_poi, poi_bounds, roverSettings, rover_start, rovHeadings
    world = World(world_bounds, numPoi, poi_bounds, roverSettings, rover_start=world_center, rovHeadings=agentInitHeadings)  # make a world

    # Create orientations for the agents outside so they will all be consist for agent i
    rewards_list = []
    for i in range(episodes): # random definition of convergence
        print 'Perfoming epidsode {0} for {1} agents...'.format(i, numAgents)
        # create random team of agent brains for the game
        teams = createTeams(nns, lenOfPool)

        team_rewards = []
        for team in teams:         
            # do the episode
            reward = doEpisode(world, team, timesteps, maxDist, minDist, mvtNoise, agentInitHeadings, rewardType, moveRandomly)
            team_rewards.append(reward)

        # Save max reward over team combos
        rewards_list.append(max(team_rewards))
       # rewards_list.append(team_rewards)  # NOT MAX! CHANGE ME BACK!
        
        # select best nn performers
        #   and mutate and replace low performers
        updateNNS(nns, egreedy * egreedyDecreaseRate)

    # outputing results
    # Find out which nns for each agent was the best
    # for row in nns:
    #     bestNN = createNN()
    #     bestNN.value = -1000000
    #     for nn in row:
    #         if nn.value > bestNN:
    #             bestNN = copy.deepcopy(nn)

    #     # For that agent, print out the weights
    #     print 'Best NN Weights:'
    #     bestNN.printWeights()

    return rewards_list


def getResults():
    ''' Runs the rover domain setup using the different sensor types:

                Sensor range: 3 types ()
                Sensor fov: 3 types (1,2,3,4) - expecting 1, 3 or 4
                Sensor noise: 3 types 
            name, xy, heading, numSens, obsRange (ignored), range - float, noise - int (0,10,50)  
            With the reward types:

                    Random, Global, Local, Difference

                With the following numbers of agents:

                        10 agents, 30 agents, 70 agents
    '''
    # .rewardType 
    # .moveRandomly 
    # .numAgents 
    # .sensorRange
    # .sensorFov 
    # .sensorNoiseInt 

    import timeit
    start_time = timeit.default_timer()
    numStatRuns = 500
    epochs = 200

    # runs all four reward types with 30 agents for 200 episodes
    # runBaseline()

    # now just select difference reward type
    baseSettings = RoverSettings(rewardType = 'DIFFERENCE',
                                  moveRandomly = False,
                                  numAgents = 5,
                                  sensorRange = 10000, # essentially inf for our world size :)
                                  sensorFov = 4, # 360 degrees
                                  sensorNoiseInt = 0 # no noise)
                                  )

    # tweaking sensor range
    sensorRangeUnlimitedSettings = copy.deepcopy(baseSettings)
    sensorRangeUnlimitedSettings.type = 'SR_Unlimited'

    sensorRangeLimitedSettings = copy.deepcopy(baseSettings)
    sensorRangeLimitedSettings.sensorRange = 10 # roughtly 10 percent of world dist
    sensorRangeLimitedSettings.type = 'SR_Limited'
    
    sensorRangeMediumSettings = copy.deepcopy(baseSettings)
    sensorRangeMediumSettings.sensorRange = 60 # over half the world dist
    sensorRangeMediumSettings.type = 'SR_Medium'

    # tweaking sensor fov
    sensorFOV360 = copy.deepcopy(baseSettings)
    sensorFOV360.type = 'SF_360'
    
    sensorFOV270 = copy.deepcopy(sensorFOV360)
    sensorFOV270.sensorFov = 3 # only 3 sensors turned on for 270deg
    sensorFOV270.type = 'SF_270'
    
    sensorFOV90 = copy.deepcopy(sensorFOV360)
    sensorFOV90.sensorFov = 1 # only sees 90 deg
    sensorFOV90.type = 'SF_90'


    # tweaking sensor noise
    sensorNoiseNone = copy.deepcopy(baseSettings)
    sensorNoiseNone.type = 'SN_0'

    sensorNoise10 = copy.deepcopy(baseSettings)
    sensorNoise10.sensorNoiseInt = 10
    sensorNoise10.type = 'SN_10'

    sensorNoise50 = copy.deepcopy(baseSettings)
    sensorNoise50.sensorNoiseInt = 50
    sensorNoise50.type = 'SN_50'


    # settings = [sensorRangeUnlimitedSettings, sensorRangeLimitedSettings, sensorRangeMediumSettings]
    settings = [sensorFOV360, sensorFOV270, sensorFOV90]
    # settings = [sensorNoiseNone, sensorNoise10, sensorNoise50]

    # baseGlobalSettings = copy.deepcopy(baseSettings)
    # baseGlobalSettings.type = 'GLOBAL'
    # baseGlobalSettings.rewardType = 'GLOBAL'

    # baseLocalSettings = copy.deepcopy(baseSettings)
    # baseLocalSettings.type = 'LOCAL'
    # baseLocalSettings.rewardType = 'LOCAL'

    # baseDifferenceSettings = copy.deepcopy(baseSettings)
    # baseDifferenceSettings.type = 'DIFFERENCE'
    # baseDifferenceSettings.rewardType = 'GLOBAL'

    # baseRandomSettings = copy.deepcopy(baseSettings)
    # baseRandomSettings.type = 'RANDOM'
    # baseRandomSettings.rewardType = 'DIFFERENCE'
    # baseRandomSettings.moveRandomly = True

    # settings = [baseGlobalSettings, baseLocalSettings, baseDifferenceSettings, baseRandomSettings]

    for i in range(numStatRuns):
        for numAgents in [10, 30, 70]:
            for x in settings:
                x.numAgents = numAgents
                rewardList = main(x, epochs)
                fname = os.getcwd() + '/results2/{0}/{1}agents/{2}statRun-RT-{3}_Eps-{4}.results'.format(x.type, numAgents, i, x.rewardType, epochs)
                print 
                print fname
                saveReward(fname, rewardList)    


    elapsed_time = timeit.default_timer() - start_time
    print str(int(elapsed_time)) + ' seconds'

def saveReward(fname, rewardList):
    d = os.path.dirname(fname)
    if not os.path.exists(d):
        os.makedirs(d)

    with open(fname, 'w') as f:
        for reward in rewardList:
            f.write(str(reward) + '\n')
        
        f.close()


def runBaseline():
    ''' Runs random, global, local, and difference with 30 agents and 200 episodes

        Returns a tuple of the lists for each analogous reward. 
    '''
    # Use random, with combinations....
    rewards_list_rand = main(RoverSettings(), episodes = 200)

    # Use global, with combinations....
    rewards_list_global = main(RoverSettings(), episodes = 200)

    # Use local, with combinations....
    rewards_list_local = main(RoverSettings(), episodes = 200)

    # Use difference, with combinations
    rewards_list_diff = main(RoverSettings(), episodes = 200)

    return (rewards_list_rand, rewards_list_global, rewards_list_local, rewards_list_diff)


if __name__ == "__main__":

    getResults()
    
#     start_time = timeit.default_timer()
# #   main(rewardType='DIFFERENCE', moveRandomly=True)  # random!
#     rewards_list = main(RoverSettings(), 10)  # learning!
#     elapsed_time = timeit.default_timer() - start_time
#     print str(int(elapsed_time)) + ' seconds'
   
#     pyplot.plot(rewards_list)
#     pyplot.show()
    # main(10, 50)
    # main(30, 50)
    # main(50, 50)
