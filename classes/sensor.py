# -*- coding: utf-8 -*-
"""
@author: Austin Nicolai
"""

class Sensor(object):
    
    # quadrant axes at 45 degree angle
    regions = {'Front': 0,
               'Left': 90,
               'Right': -90,
               'Back': 180}    
    
    def __init__(self, sector, location, rover_heading, sensor_range, sensor_noise):
        # initialize
        self.location = location

        # define quadrant edges in terms of degrees
        global_heading = rover_heading + self.regions['Front']
        self.left_edge = global_heading + 45
        self.right_edge = global_heading - 45
        
        # check for roll-over
        if self.left_edge > 359:
            self.left_edge -= 360
            
        if self.right_edge > 359:
            self.right_edge -= 360
        
        # define sensor characteristics
        self.sensor_range = sensor_range
        self.sensor_noise = sensor_noise
        
    def updateFieldOfView(self, sector, rover_heading):
        # define quadrant edges in terms of degrees
        global_heading = rover_heading + self.regions[sector]
        self.left_edge = global_heading + 45
        self.right_edge = global_heading - 45
        
        # check for roll-over
        if self.left_edge > 359:
            self.left_edge -= 360
            
        if self.right_edge > 359:
            self.right_edge -= 360