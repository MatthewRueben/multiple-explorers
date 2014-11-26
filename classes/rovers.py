# -*- coding: utf-8 -*-
"""
@author: Austin Nicolai
"""

from POI_sensor import POI_Sensor
from rover_sensor import Rover_Sensor
import math

#TODO: remove Location class and import at some point

class Location:
    """ A point in 2D Euclidean space. """
    def __init__(self, x, y):
        self.x = x
        self.y = y
        
    def __str__(self):
        return 'Location: (' + str(self.x) + ',' + str(self.y) + ')'
    
    def __eq__(self, other):
        if isinstance(other, Location):
            if self.x == other.x and self.y == other.y:
                return True
            return False

    def __sub__(self, subtrahend):
        """ Subtraction for Locations = Euclidean distance between the Location and the subtrahend.
        Only works if the subtrahend class is "Location". """
        if isinstance(subtrahend, Location):
            dx = subtrahend.x
            dy = subtrahend.y
        else:  # assume the other class has an attribute "location" of class "Location"
            dx = subtrahend.location.x
            dy = subtrahend.location.y

        return math.sqrt((self.x - dx) ** 2 + (self.y - dy) ** 2)


class Rover():
        
    max_sensors = 4
    sensor_regions = ['Front', 'Left', 'Right', 'Back']        
        
    def __init__(self, name, x, y, heading, num_sensors, sensor_range, sensor_noise, num_POI):
        self.name = name
        self.location = Location(x, y)
        self.heading = 0 # in radians
        self.sensor_range = sensor_range
        self.sensor_noise = sensor_noise
        self.heading = heading        
        self.num_sensors = num_sensors
        self.fov = 90 * num_sensors # in degrees
        self.POI_table = [1000] * num_POI # initialize arbitrarily large compared to world

        # set up sensors
        self.POI_sensors = []
        self.rover_sensors = []        
    
        # max of 4 sensors
        if self.num_sensors > self.max_sensors:
            self.num_sensors = self.max_sensors
            
        for i in xrange(self.num_sensors):
            self.POI_sensors.append(POI_Sensor(self.sensor_regions[i], self.heading, self.location, sensor_range, sensor_noise))
            self.rover_sensors.append(Rover_Sensor(self.sensor_regions[i], self.heading, self.location, sensor_range, sensor_noise))
       
    def takeAction(self, dx, dy):
        # movement noise built into function input
        
        # find components of dx
        dx_x = math.sin(90 - self.heading) * dx
        dx_y = math.cos(90 - self.heading) * dx
        
        # find components of dy
        dy_x = math.sin(self.heading) * dy
        dy_y = math.cos(self.heading) * dy
            
        # update the rover position
        self.location.x += dx_x
        self.location.x += dy_x
        
        self.location.y += dx_y
        self.location.y += dy_y
    
        # update orientation/sensor boundaries
        new_heading = math.atan(dy/dx) * 180. / math.pi
        
        for i in xrange(self.num_sensors):
            self.POI_sensors[i].updateFieldOfView(self.sensor_regions[i], new_heading)
            self.rover_sensors[i].updateFieldOfView(self.sensor_regions[i], new_heading)
    
    
    def updatePoiTable(self, POI_list):
        # iterate over all POIs
        for poi in POI_list:
            distance = self.location - POI_list[poi]
            
            # if closest observation and in sensor range: update the POI table
            if (distance < self.POI_table[poi]) and (distance < self.sensor_range):
                self.POI_table[poi] = distance
                
        
    def getNNInputs(self, POI_list, min_observation_dist, rover_list):
        # return all POI and rover counts in format:
        #   [Q1 POI, Q2 POI, Q3 POI, Q4 POI, Q1 Rover, Q2 Rover, Q3 Rover, Q4 Rover]
        rover_count = 0        
        poi_count = 0
        output_list = []
        
        for i in xrange(len(self.sensor_regions)):
            # check if valid quadrant            
            if i > self.num_sensors:
                output_list.append(0) # if no sensor for the quadrant, return 0
                break
            
            # get count
            poi_count = self.POI_sensors[i].getPoiCount(POI_list, min_observation_dist)
            output_list.append(poi_count)
            
        for i in xrange(len(self.sensor_regions)):
            # check if valid quadrant
            if i > self.num_sensors:
                output_list.append(0) # if no sensor for the quadrant, return 0
                break
            
            # get count
            rover_count = self.rover_sensors[i].getRoverCount(rover_list)
            output_list.append(rover_count)
    
        return output_list