# -*- coding: utf-8 -*-
"""
@author: Austin Nicolai
"""

from POI_sensor import POI_Sensor
from rover_sensor import Rover_Sensor
from geography import Location
import math
import copy
import sys


class Rover():
        
    max_sensors = 4
    sensor_regions = ['Front', 'Left', 'Right', 'Back']        
        
    def __init__(self, name, x, y, heading, num_sensors, observation_range, sensor_range, sensor_noise, num_POI):
        self.name = name
        self.reset(x, y, heading)  # reset to starting location
        self.heading = 0 # in degrees
        self.sensor_range = sensor_range
        self.sensor_noise = sensor_noise
        self.heading = heading 
        # self.heading = 90       
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
            #print "Sensor Region: ", self.sensor_regions[i]
            self.POI_sensors.append(POI_Sensor(self.sensor_regions[i], self.location, self.heading, sensor_range, sensor_noise))
            self.rover_sensors.append(Rover_Sensor(self.sensor_regions[i], self.location, self.heading, observation_range, sensor_range, sensor_noise))

       
    def save_location(self):
        # save current location to history!
        self.location_history.append(copy.deepcopy(self.location))  
        

    def reset(self, x, y, heading):
        # reset to the starting location
        self.location_history = []  # clear the history. history won't include the starting location
        self.location = Location(x, y)
        self.heading = heading


    def takeAction(self, dx, dy):
        # movement noise built into function input
        
        # # find components of dx
        dx_x = math.sin(90 - self.heading) * dx
        dx_y = math.cos(90 - self.heading) * dx
        
        # # find components of dy
        dy_x = math.sin(self.heading) * dy
        dy_y = math.cos(self.heading) * dy
            
        # update the rover position
        self.location.x += dx_x
        self.location.x += dy_x
        
        self.location.y += dx_y
        self.location.y += dy_y
        # print 'Rover location before in ta ', self.location
        # self.location.y += dy 
        # self.location.x += dx
        self.save_location()  # save it!
        # print 'Rover location after in ta ', self.location
    
        # update orientation/sensor boundaries
        if dx == 0:  # don't divide by zero!
            dx = sys.float_info.min
        new_heading = math.atan2(self.location.y, self.location.x) * 180. / math.pi
        # new_heading = 90
        
        for i in xrange(self.num_sensors):
            self.POI_sensors[i].updateFieldOfView(self.sensor_regions[i], new_heading)
            self.POI_sensors[i].updateLocation(self.location)
            self.rover_sensors[i].updateFieldOfView(self.sensor_regions[i], new_heading)
            self.rover_sensors[i].updateLocation(self.location)

    
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
            # reset value
            poi_count = 0

            # check if valid quadrant
            if i >= self.num_sensors:
                output_list.append(0) # if no sensor for the quadrant, return 0

            else:
                # get count
                poi_count = self.POI_sensors[i].getPoiCount(POI_list, min_observation_dist)
                output_list.append(poi_count)
        
        for i in xrange(len(self.sensor_regions)):
            # reset value
            rover_count = 0

            # check if valid quadrant
            if i >= self.num_sensors:
                output_list.append(0) # if no sensor for the quadrant, return 0
            else:
                # get count
                rover_count = self.rover_sensors[i].getRoverCount(rover_list, min_observation_dist)
                output_list.append(rover_count)
    
        return output_list


    def getObservableRovers(self, rover_list):
        # return a list of indices for rovers visibile
        observable_rovers = []
        
        for i in xrange(len(self.sensor_regions)):
            # check if valid quadrant
            if i <= self.num_sensors:
                temp_rovers = self.rover_sensors[i].getObservableRovers(rover_list)
                
                # append all returned indices                
                for j in temp_rovers:
                    observable_rovers.append(temp_rovers[j])
                    
        return obersable_rovers
