#!/usr/bin/env python
# does my comment and committ work?

import random

class World():
    def __init__(self, N_poi, poi_bounds):
        """ Input "poi_bounds" is of class "2DBounds". """
        V_bounds = (0.0, 1.0)  # FIX ME?
        self.poi_bounds = poi_bounds
        self.POIs = []
        for poi_index in range(N_poi):
            V_choice = random.uniform(V_bounds[0], V_bounds[1])
            poi = POI(V_choice)  # assign POI value
            self.POIs.append(poi)
        
    def reset(self):
        for poi in self.POIs:
            poi.place_randomly(self.poi_bounds)  # assign POI location


import random

class 2DBounds():
    def __init__(self, (x_lower, x_upper), (y_lower, y_upper)):
        self.x_lower = x_lower
        self.x_upper = x_upper

        self.y_lower = y_lower
        self.y_upper = y_upper

    def random_within_bounds(self):
        x_choice = random.uniform(self.x_lower, self.x_upper)
        y_choice = random.uniform(self.y_lower, self.y_upper)
        return (x_choice, y_choice)


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

