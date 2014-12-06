# -*- coding: utf-8 -*-
"""
@author: Austin Nicolai
"""

import sys
from sensor import Sensor
import math
from random import randint

class POI_Sensor(Sensor):
    
    def __init__(self, sector, location, rover_heading, sensor_range, sensor_noise):
        super(POI_Sensor, self).__init__(sector, location, rover_heading, sensor_range, sensor_noise)
        
        
    def getPoiCount(self, POI_list, min_observation_dist):
        # determine the total rovers seen
        POI_count = 0
        
        # loop over all rovers
        for poi in POI_list:
            # determine the distance to the rover            
            distance = self.location - poi.location
            # print 'Distance in poi count ', distance
            
            # add sensor noise to the distance
            random_noise = randint(-self.sensor_noise, self.sensor_noise)
            distance = distance * (1. + random_noise/100.)
            
            # determine the angle to the rover
            dx = poi.location.x - self.location.x
            dy = poi.location.y - self.location.y
            if dx == 0:
                dx = sys.float_info.min
            angle = math.atan2(dy, dx)
            angle = angle * 180. / math.pi # convert to degrees
            
            # ensure angle in range [0, 360]
            if angle < 0:
                angle += 360
                
            # angle range is: [left_edge, right_edge)

            # if distance is 0, the POI is on top of the rover and can be seen:
            if distance == 0:
                sum_dist = max(distance**2, min_observation_dist**2)
                POI_count += (poi.V/sum_dist)
            # if angle range straddles 0:
            elif (self.left_edge < 90) and (self.right_edge > 270):
                if (distance <= self.sensor_range) and ((0 <= angle <= self.left_edge) or (360 > angle > self.right_edge)):
                    sum_dist = max(distance**2, min_observation_dist**2)
                    POI_count += (poi.V/sum_dist)
            # if angle range is typical:
            elif (distance <= self.sensor_range) and (self.right_edge < angle <= self.left_edge):
                sum_dist = max(distance**2, min_observation_dist**2)
                POI_count += (poi.V/sum_dist)

        return POI_count
