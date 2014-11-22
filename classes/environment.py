#!/usr/bin/env python
# does my comment and committ work?

import random
from matplotlib import pyplot

class World():
    def __init__(self, world_bounds, N_poi, poi_bounds):
        """ Inputs "world_bounds" and "poi_bounds" are of class "2DBounds". """
        V_bounds = (0.0, 1.0)  # FIX ME?
        self.world_bounds = world_bounds
        self.poi_bounds = poi_bounds
        self.POIs = []
        for poi_index in range(N_poi):
            V_choice = random.uniform(V_bounds[0], V_bounds[1])
            poi = POI(V_choice)  # assign POI value
            self.POIs.append(poi)
        
    def reset(self):
        for poi in self.POIs:
            poi.place_randomly(self.poi_bounds)  # assign POI location

    def test_plot(self):
        pyplot.ion()
        pyplot.cla()
        for poi in self.POIs:
            pyplot.plot(poi.location.x, poi.location.y, 'k*')
        pyplot.axis([self.world_bounds.x_lower, self.world_bounds.x_upper, 
                     self.world_bounds.y_lower, self.world_bounds.y_upper])
        pyplot.draw()


import random

class Bounds2D():
    def __init__(self, (x_lower, x_upper), (y_lower, y_upper)):
        self.x_lower = x_lower
        self.x_upper = x_upper

        self.y_lower = y_lower
        self.y_upper = y_upper

    def random_within_bounds(self):
        x_choice = random.uniform(self.x_lower, self.x_upper)
        y_choice = random.uniform(self.y_lower, self.y_upper)
        return (x_choice, y_choice)

    def get_center(self):
        x_center = (self.x_lower + self.x_upper) / 2
        y_center = (self.y_lower + self.y_upper) / 2
        return (x_center, y_center)

    def __str__(self):
        return str(((self.x_lower, self.x_upper), 
                    (self.y_lower, self.y_upper)))

    #def __add__(self, addend):
    #    """ Addition for 2DBounds classes is just attribute-by-attribute. """
    #    x_lower = self.x_lower + addend.x_lower
    #    x_upper = self.x_upper + addend.x_upper
    #
    #    y_lower = self.y_lower + addend.y_lower
    #    y_upper = self.y_upper + addend.y_upper
    #
    #    return 2DBounds((x_lower, x_upper), (y_lower, y_upper))
        


import random

class POI():
    def __init__(self, V):
        self.V = V  # POI value

    def place_randomly(self, bounds):
        x, y  = bounds.random_within_bounds()
        self.location = Location(x, y)

    def __sub__(self, subtrahend):
        """ Subtraction for POIs = Euclidean distance between the POI and the subtrahend.
        Only works if the subtrahend class has attribute "location" of class "Location". """
        return self.location - other_poi.location


import math

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

    def __sub__(self, other_location):
        """ Subtraction for Locations = Euclidean distance between the Location and the subtrahend.
        Only works if the subtrahend class is "Location". """
        return math.sqrt((self.x - other_location.x) ** 2 + (self.y - other_location.y) ** 2)

