# -*- coding: utf-8 -*-
"""
@author: Austin Nicolai
"""

from sensor import Sensor
import math

class POI_Sensor(Sensor):
    
    def __init__(self, sector, location, rover_heading, sensor_range, sensor_noise):
        super(POI_Sensor, self).__init__(sector, location, rover_heading, sensor_range, sensor_noise)

    def getPoiCount(self, POI_list, min_observation_dist):
        # determine the total rovers seen
        POI_count = 0
        
        # loop over all rovers
        for poi in POI_list:
            # determine the distance to the rover            
            distance = self.location - POI_list[poi].location
            
            # add sensor noise to the distance
            distance = distance * (1 + self.sensor_noise)
            
            # determine the angle to the rover
            dx = self.location.x - POI_list[poi].location.x
            dy = self.location.y - POI_list[poi].location.y
            angle = math.atan(dy/dx)
            angle = angle * 180. / math.pi # convert to degrees
            
            # ensure angle in range [0, 360]
            if angle < 0:
                angle += 360

            # angle range is: [left_edge, right_edge)
            
            # if angle range straddles 0:
            if (distance <= self.sensor_range) and (0 <= angle <= self.left_edge) and (360 > angle > self.right_edge):
                sum_dist = max(distance**2, min_observation_dist**2)
                POI_count += (POI_list[poi].V/sum_dist)
            # if angle range is typical:
            elif (distance <= self.sensor_range) and (angle <= self.left_edge) and (angle > self.right_edge):
                sum_dist = max(distance**2, min_observation_dist**2)
                POI_count += (POI_list[poi].V/sum_dist)
            
        return POI_count
