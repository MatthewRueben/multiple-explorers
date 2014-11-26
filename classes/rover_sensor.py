# -*- coding: utf-8 -*-
"""
@author: Austin Nicolai
"""

from sensor import Sensor
import math

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
            distance = self.location - rover_list[rover].location
            
            # add sensor noise to the distance
            distance = distance * (1. + self.sensor_noise/100.)
            
            # determine the angle to the rover
            dx = self.location.x - rover_list[rover].location.x
            dy = self.location.y - rover_list[rover].location.y
            angle = math.atan(dy/dx)
            angle = angle * 180. / math.pi # convert to degrees
            
            # ensure angle in range [0, 360]
            if angle < 0:
                angle += 360

            # angle range is: [left_edge, right_edge)
            
            # if distance is 0, the rovers are on top of eachother and can be seen:
            if distance == 0:
                sum_dist = max(distance**2, min_observation_dist**2)
                rover_count += (1/sum_dist)
            # if angle range straddles 0:
            elif (distance <= self.senor_range) and (0 <= angle <= self.left_edge) and (360 > angle > self.right_edge):
                sum_dist = max(distance**2, min_observation_dist**2)
                rover_count += (1/sum_dist)
            # if angle range is typical:
            elif (distance <= self.sensor_range) and (angle <= self.left_edge) and (angle > self.right_edge):
                sum_dist = max(distance**2, min_observation_dist**2)
                rover_count += (1/sum_dist)
            
        return rover_count
        
        
    def getObservableRovers(self, rover_list):
        # determine the observable rovers
        rover_indices = []
        
        # loop over all rovers
        for rover in rover_list:
            # determine the distance to the rover            
            distance = self.location - rover_list[rover].location
            
            # add sensor noise to the distance
            distance = distance * (1. + self.sensor_noise/100.)
            
            # determine the angle to the rover
            dx = self.location.x - rover_list[rover].location.x
            dy = self.location.y - rover_list[rover].location.y
            angle = math.atan(dy/dx)
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