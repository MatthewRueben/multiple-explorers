#!/usr/bin/env python
# does my comment and committ work?

import random
from matplotlib import pyplot

class World():
    def __init__(self, world_bounds, N_poi, poi_bounds, N_rovers, rover_start):
        """ Inputs "world_bounds" and "poi_bounds" are of class "2DBounds". """
        V_bounds = (0.0, 1.0)  # FIX ME?
        self.world_bounds = world_bounds
        self.poi_bounds = poi_bounds

        # Init POIs
        self.POIs = []
        for poi_index in range(N_poi):
            V_choice = random.uniform(V_bounds[0], V_bounds[1])
            poi = POI(V_choice, d_min=5.0)  # assign POI value & minimum observation distance
            self.POIs.append(poi)

        # Init rovers
        self.rovers = []
        for rover_index in range(N_rovers):
            dx = random.uniform(-35, 35)  # FOR TESTING ONLY!
            dy = random.uniform(-35, 35)  # FOR TESTING ONLY
            rover = DummyRover(rover_start.x + dx, 
                               rover_start.y + dy)  # FOR TESTING ONLY!
            self.rovers.append(rover)
        
    def reset(self):
        for poi in self.POIs:
            poi.place_randomly(self.poi_bounds)  # assign POI location
            
    def get_rewards(self):
        reward = 0
        rover_closest_list = []
        for poi in self.POIs:
            delta_min = 100.0  # start arbitrarily high
            rover_closest = None
            for rover_index, rover in enumerate(self.rovers):
                delta = (rover.location - poi)  # observation distance
                if delta < delta_min:
                    delta_min = delta
                    rover_closest = rover_index
            delta_min = min(delta_min ** 2, poi.d_min ** 2)  # delta is actually the SQUARED Euclidean distance
            rover_closest_list.append(rover_closest)
            reward += poi.V / delta_min
        return reward, rover_closest_list

    def test_plot(self, rover_closest_list=[]):
        pyplot.ion()
        pyplot.cla()
        for poi in self.POIs:
            pyplot.plot(poi.location.x, poi.location.y, 'k*')
        for rover in self.rovers:
            pyplot.plot(rover.location.x, rover.location.y, 'ro')
        pyplot.axis([self.world_bounds.x_lower, self.world_bounds.x_upper, 
                     self.world_bounds.y_lower, self.world_bounds.y_upper])
        if len(rover_closest_list) > 0:
            for poi_index, rover_closest in enumerate(rover_closest_list):
                pyplot.plot([self.rovers[rover_closest].location.x, self.POIs[poi_index].location.x],
                            [self.rovers[rover_closest].location.y, self.POIs[poi_index].location.y])
        pyplot.draw()


class DummyRover():
    def __init__(self, x, y):
        self.location = Location(x, y)


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

