#!/usr/bin/env python

import random
from matplotlib import pyplot

class World():
    def __init__(self, world_bounds, N_poi, poi_bounds, N_rovers, rover_start):
        """ Inputs "world_bounds" and "poi_bounds" are of class "2DBounds". """
        V_bounds = (0.0, 1.0)  # FIX ME?
        self.world_bounds = world_bounds
        self.poi_bounds = poi_bounds
        self.rover_start = rover_start

        # Init POIs
        self.POIs = []
        for poi_index in range(N_poi):
            V_choice = random.uniform(V_bounds[0], V_bounds[1])
            poi = POI(V_choice, d_min=5.0)  # assign POI value & minimum observation distance
            self.POIs.append(poi)

        # Init rovers
        self.rovers = []
        for rover_index in range(N_rovers):
            rover = DummyRover(self.rover_start.x, 
                               self.rover_start.y)  # FOR TESTING ONLY!
            self.rovers.append(rover)
        
    def reset(self):
        for poi in self.POIs:
            poi.place_randomly(self.poi_bounds)  # assign POI location
        for rover in self.rovers:
            rover.reset(self.rover_start.x,
                        self.rover_start.y)
            
    def get_rewards(self):
        rewards = {'POI': [],
                   'GLOBAL': 0, 
                   'LOCAL': [0]*len(self.rovers), 
                   'DIFFERENCE': [0]*len(self.rovers)}
        rover_closest_list = []

        # Calculate GLOBAL and LOCAL rewards
        for poi_index in range(len(self.POIs)):  # for each POI, figure out which rover is closest and get the appropriate reward
            delta_min, rover_closest = self.find_closest(poi_index)
            rover_closest_list.append(rover_closest)
            poi_reward = self.POIs[poi_index].V / delta_min  # the entire reward for this POI
            rewards['POI'].append(poi_reward)  # keep track of the reward for each POI
            rewards['LOCAL'][rover_closest[0]] += poi_reward  # add to closest rover's local reward
            rewards['GLOBAL'] += poi_reward

        # Calculate DIFFERENCE reward (with counterfactual c = 0)
        for my_rover_index, rover in enumerate(self.rovers):
            G_without = rewards['GLOBAL']  # Set G(Z_-i) = G(Z)
            closest_to = [poi_index for poi_index, (rover_index, step_index) in enumerate(rover_closest_list) if rover_index == my_rover_index]  # find which POIs this rover was closest to
            for poi_index in closest_to:  # for each of those POIs...
                G_without -= rewards['POI'][poi_index]  # Subtract its old reward
                delta_min_new, rover_closest_new = self.find_closest(poi_index, my_rover_index)  # Find the next-closest rover to it
                poi_reward_new = self.POIs[poi_index].V / delta_min_new  # Calculate its new reward
                G_without += poi_reward_new   # Add it back in (G_without should be getting smaller)
            rewards['DIFFERENCE'][my_rover_index] = rewards['GLOBAL'] - G_without # Calculate D = G(Z) - G(Z_-i)

        return rewards, rover_closest_list


    def find_closest(self, poi_index, not_this_rover=None):
        """ Finds closest rover to the specified POI. 
        Returns that rover's index as well as the distance metric. """
        poi = self.POIs[poi_index]
        delta_min = 100.0  # start arbitrarily high
        rover_closest = None
        step_closest = None
        for rover_index, rover in enumerate(self.rovers):
            if rover_index is not not_this_rover:
                for step_index, location in enumerate(self.rovers[rover_index].location_history):
                    delta = (location - poi)  # observation distance
                    if delta < delta_min:  # the closest rover counts, even if it's closer than the minimum observation distance
                        delta_min = delta
                        rover_closest = (rover_index, step_index)
        delta_min = min(delta_min ** 2, poi.d_min ** 2)  # delta is actually the SQUARED Euclidean distance
        return delta_min, rover_closest


    def test_plot(self, rover_closest_list=[]):
        import time
        pyplot.ion()
        
        # Plot each rover's trajectory, one by one
        for this_rover_index, rover in enumerate(self.rovers):

            pyplot.cla()  # clear axis
            pyplot.title('Rover #' + str(this_rover_index + 1))

            # Plot the world, with POIs
            for poi in self.POIs:
                pyplot.plot(poi.location.x, poi.location.y, 'k*')
            pyplot.axis([self.world_bounds.x_lower, self.world_bounds.x_upper, 
                         self.world_bounds.y_lower, self.world_bounds.y_upper])

            trajectory_x = [step.x for step in rover.location_history]
            trajectory_y = [step.y for step in rover.location_history]
            pyplot.plot(trajectory_x, trajectory_y, 'ro-')

            # Draw lines to indicate whenever the rover became the closest observer of a POI
            if rover_closest_list:
                closest_to = [(poi_index, step_index) for poi_index, (rover_index, step_index) in enumerate(rover_closest_list) if rover_index == this_rover_index]  # find which POIs this rover was closest to
                for (poi_index, step_index) in closest_to:  # for each of those POIs...
                    pyplot.plot([trajectory_x[step_index], self.POIs[poi_index].location.x],
                                [trajectory_y[step_index], self.POIs[poi_index].location.y])
            pyplot.draw()
            time.sleep(1.0)


import copy

class DummyRover():
    def __init__(self, x, y):
        self.location_history = []  # locations I've been this episode
        self.reset(x, y)

    def save_location(self):
        self.location_history.append(copy.deepcopy(self.location))  # save current location to history!
        
    def act(self, action=None):
        choices = range(-15, 15)
        self.location.x += random.choice(choices)
        self.location.y += random.choice(choices)
        self.save_location()  # be sure to save your new location afterwards so you can get a reward
        
    def reset(self, x, y):
        self.location = Location(x, y)
        self.save_location()


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

