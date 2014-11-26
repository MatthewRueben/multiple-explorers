#!/usr/bin/env python

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


import random

class POI():
    def __init__(self, V, d_min):
        self.V = V  # POI value
        self.d_min = d_min

    def place_randomly(self, bounds):
        x, y  = bounds.random_within_bounds()
        self.location = Location(x, y)

    def __str__(self):
        return 'POI: Value: ' + str(self.V) + ', ' + str(self.location)
    
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

