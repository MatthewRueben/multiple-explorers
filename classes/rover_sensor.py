# -*- coding: utf-8 -*-
"""
@author: Austin Nicolai
"""

import sys
from sensor import Sensor
import math
from random import randint

class Rover_Sensor(Sensor):
    
    def __init__(self, sector, location, rover_heading, observation_range, sensor_range, sensor_noise):
        super(Rover_Sensor, self).__init__(sector, location, rover_heading, sensor_range, sensor_noise)
        
        self.observation_range = observation_range
        
        
    def getRoverCount(self, rover_list, min_observation_dist):
        # determine the total rovers seen
        rover_count = 0
        
        # loop over all rovers
        for rover in rover_list:
            # determine the distance to the rover            
            distance = self.location - rover.location
            
            # add sensor noise to the distance
            random_noise = randint(-self.sensor_noise, self.sensor_noise)
            distance = distance * (1. + random_noise/100.)
            
            # determine the angle to the rover
            dx = rover.location.x - self.location.x
            dy = rover.location.y - self.location.y
            if dx == 0:  # exception for rovers that are on top of each other (or identical)
                dx = sys.float_info.min
            angle = math.atan2(dy, dx)
            angle = angle * 180. / math.pi # convert to degrees
            
            # ensure angle in range [0, 360]
            if angle < 0:
                angle += 360

            # angle range is: [left_edge, right_edge)
            
            # if distance is 0, the rovers are on top of eachother and can be seen:
            if distance == 0:
                sum_dist = max(distance**2, min_observation_dist**2)
                rover_count += (1./sum_dist)
            # if angle range straddles 0:
            elif (self.left_edge < 90) and (self.right_edge > 270):
                if (distance <= self.sensor_range) and ((0 <= angle <= self.left_edge) or (360 > angle > self.right_edge)):
                    sum_dist = max(distance**2, min_observation_dist**2)
                    rover_count += (1./sum_dist)
            # if angle range is typical:
            elif (distance <= self.sensor_range) and (self.right_edge < angle <= self.left_edge):
                sum_dist = max(distance**2, min_observation_dist**2)
                rover_count += (1./sum_dist)
            
        return rover_count
        
        
    def getObservableRovers(self, rover_list):
        # determine the observable rovers
        rover_indices = []
        
        # loop over all rovers
        for rover in rover_list:
            # determine the distance to the rover            
            distance = self.location - rover.location
            
            # add sensor noise to the distance
            distance = distance * (1. + self.sensor_noise/100.)
            
            # determine the angle to the rover
            dx = self.location.x - rover.location.x
            dy = self.location.y - rover.location.y
            if dx == 0:
                dx = sys.float_info.min
            angle = math.atan2(dy, dx)
            angle = angle * 180. / math.pi # convert to degrees
            
            # ensure angle in range [0, 360]
            if angle < 0:
                angle += 360

            # angle range is: [left_edge, right_edge)
            
            # if distance is 0, the rovers are on top of eachother and can be seen:
            if distance == 0:
                rover_indices.append(rover)
            # if angle range straddles 0:
            elif (distance <= self.observation_range) and (0 <= angle <= self.left_edge) and (360 > angle > self.right_edge):
                rover_indices.append(rover)
            # if angle range is typical:
            elif (distance <= self.observation_range) and (angle <= self.left_edge) and (angle > self.right_edge):
                rover_indices.append(rover)
            
        return rover_indices
