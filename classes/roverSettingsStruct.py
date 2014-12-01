#!/usr/bin/env python

class RoverSettings():
    ''' Class/Structure for the rover settings.
        Specifies: rewardType, moveRandomly, numAgents, sensorRange, sensorFov, noiseInt
    '''
    def __init__(self, rewardType = 'DIFFERENCE', moveRandomly = False, numAgents = 30, sensorRange = 10000, sensorFov = 4, sensorNoiseInt = 0):
        self.rewardType = rewardType
        self.moveRandomly = moveRandomly
        self.numAgents = numAgents
        self.sensorRange = sensorRange
        self.sensorFov = sensorFov
        self.sensorNoiseInt = sensorNoiseInt