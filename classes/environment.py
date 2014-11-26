#!/usr/bin/env python

from geography import Bounds2D, Location, POI
from rovers import Rover
import random
import itertools
from matplotlib import pyplot

class World():
    def __init__(self, world_bounds, N_poi, poi_bounds, N_rovers, rover_start, rovHeadings):
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
        for rover_index, heading in itertools.izip(range(N_rovers), rovHeadings):
            rover = Rover(name='Fred',
                          x=self.rover_start.x, 
                          y=self.rover_start.y,
                          heading=heading,
                          num_sensors=4,
                          sensor_range=1000.0,  # ~infinite
                          sensor_noise=0.10,  # 10%
                          num_POI=100)
            self.rovers.append(rover)
        
    def reset(self, headings):
        for poi in self.POIs:
            poi.place_randomly(self.poi_bounds)  # assign POI location
        for rover, heading in itertools.izip(self.rovers, headings):
            # reset agents to be center of world
            rover.reset(self.rover_start.x,
                        self.rover_start.y,
                        heading)

            
    def get_rewards(self):
        rewards = {'POI': [],
                   'GLOBAL': 0, 
                   'LOCAL': [0]*len(self.rovers), 
                   'DIFFERENCE': [0]*len(self.rovers),
                   'DIFFERENCE_PO': [0]*len(self.rovers)}
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
                delta_min_new, rover_closest_new = self.find_closest(poi_index, [my_rover_index])  # Find the next-closest rover to it
                poi_reward_new = self.POIs[poi_index].V / delta_min_new  # Calculate its new reward
                G_without += poi_reward_new   # Add it back in (G_without should be getting smaller)
            rewards['DIFFERENCE'][my_rover_index] = rewards['GLOBAL'] - G_without # Calculate D = G(Z) - G(Z_-i)

            
        # Calculate DIFFERENCE reward with PARTIAL OBSERVABILITY (and c = 0)
        """
        # for each rover
         # find which rovers this rover can see
         # it can see itself! very important
         # start with the full-observability POI rewards
         # for each POI
                # Partial Observability
                G_PO -= rewards['POI'][poi_index]  # Subtract its old reward
                delta_min_new, rover_closest_new = self.find_closest(poi_index, [my_rover_index])  # Find the next-closest rover to it
                poi_reward_new = self.POIs[poi_index].V / delta_min_new  # Calculate its new reward
                G_PO += poi_reward_new   # Add it back in (G_without should be getting smaller)

                # Without this agent
                G_PO_without
                delta_min_new, rover_closest_new = self.find_closest(poi_index, [my_rover_index])  # Find the next-closest rover to it
                poi_reward_new = self.POIs[poi_index].V / delta_min_new  # Calculate its new reward
                G_PO_without

            rewards['DIFFERENCE_PO'][my_rover_index] = G_PO - G_PO_without  # Calculate D_PO
        """

        return rewards, rover_closest_list


    def find_closest(self, poi_index, not_these_rovers=[], not_these_times=[]):
        """ Finds closest rover to the specified POI. 
        Returns that rover's index as well as the distance metric. """
        if not not_these_times:  # if no time restrictions are provided
            not_these_times = [[]]*len(not_these_rovers)
        poi = self.POIs[poi_index]
        delta_min = 100.0  # start arbitrarily high
        rover_closest = None
        step_closest = None
        for rover_index, rover in enumerate(self.rovers):

            # Decide what to skip
            skip_rover = False
            if rover_index in not_these_rovers:  # if this rover is on the skip list
                ignored_rover_index = not_these_rovers.index(rover_index)
                steps_to_skip = not_these_times[ignored_rover_index]  # get the times to skip
                skip_rover = bool(skip_steps)  # skip this entire rover if no particular time steps are specified
            else:
                steps_to_skip = []

            # Check observation distances for the rover locations we aren't skipping
            if not skip_rover:
                for step_index, location in enumerate(self.rovers[rover_index].location_history):
                    if step_index not in steps_to_skip:
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
