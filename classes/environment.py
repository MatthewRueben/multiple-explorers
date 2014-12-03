#!/usr/bin/env python

from geography import Bounds2D, Location, POI
from rovers import Rover
from roverSettingsStruct import RoverSettings
import random
import itertools
from matplotlib import pyplot
import copy

class World():
    def __init__(self, world_bounds, N_poi, poi_bounds, rover_settings, rover_start, rovHeadings):
        """ Inputs "world_bounds" and "poi_bounds" are of class "2DBounds". """
        # Rover settings attributes:
        # .rewardType 
        # .moveRandomly 
        # .numAgents 
        # .sensorRange
        # .sensorFov 
        # .sensorNoiseInt 
        N_rovers = rover_settings.numAgents


        self.world_bounds = world_bounds
        self.poi_bounds = poi_bounds
        self.rover_start = rover_start

        # Init POIs
        self.POIs = []
        total_val = 450.0
        leftover_val = 450.0
        for poi_index in range(N_poi):
            # V_choice = random.uniform(V_bounds[0], V_bounds[1])
            poi_value = random.randint(0, leftover_val)
            leftover_val -= poi_value 
            poi = POI(poi_value, d_min=5.0)  # assign POI value & minimum observation distance
            self.POIs.append(poi)

        # Init rovers
        self.rovers = []
        for rover_index, heading in itertools.izip(range(N_rovers), rovHeadings):
            rover = Rover(name='Fred',
                          x=self.rover_start.x, 
                          y=self.rover_start.y,
                          heading=heading,
                          num_sensors=rover_settings.sensorFov,
                          observation_range=10,
                          sensor_range=rover_settings.sensorRange,  
                          sensor_noise=rover_settings.sensorNoiseInt,  
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

        # Calculate GLOBAL reward
        for poi_index in range(len(self.POIs)):  # for each POI, figure out which rover is closest and get the appropriate reward
            delta_min, rover_closest = self.find_closest(poi_index)
            # print 'Closest rover: ', rover_closest
            rover_closest_list.append(rover_closest)
            poi_reward = self.POIs[poi_index].V / delta_min  # the entire reward for this POI
            # print '  Poi reward: ', poi_reward
            # print
            rewards['POI'].append(poi_reward)  # keep track of the reward for each POI
            rewards['GLOBAL'] += poi_reward

        # Calculate LOCAL reward
        for rover_index, rover in enumerate(self.rovers):
            rewards['LOCAL'][rover_index] = 0
            for poi_index, poi in enumerate(self.POIs):  # for each POI...
                delta_min = 100.0  # start arbitrarily high
                for step_index, location in enumerate(rover.location_history):  # check each of the rover's steps
                    delta = (location - poi)  # observation distance
                    if delta < delta_min:  # the closest distance counts, even if it's closer than the minimum observation distance
                        delta_min = delta
                delta_min = max(delta_min ** 2, poi.d_min ** 2)  # delta is actually the SQUARED Euclidean distance
                poi_reward = poi.V / delta_min  # the entire reward for this POI (for this rover only)
                rewards['LOCAL'][rover_index] += poi_reward

        # Calculate DIFFERENCE reward (with counterfactual c = 0)
        for my_rover_index, rover in enumerate(self.rovers):
            G_without = rewards['GLOBAL']  # Set G(Z_-i) = G(Z)
            closest_to = [poi_index for poi_index, (rover_index, step_index) in enumerate(rover_closest_list) if rover_index == my_rover_index]  # find which POIs this rover was closest to
            for poi_index in closest_to:  # for each of those POIs...
                G_without -= rewards['POI'][poi_index]  # Subtract its old reward
                delta_min_new, rover_closest_new = self.find_closest(poi_index, [my_rover_index])  # Find the next-closest rover to it
                #print (rover_closest_list[poi_index], rover_closest_new)
                poi_reward_new = self.POIs[poi_index].V / delta_min_new  # Calculate its new reward
                G_without += poi_reward_new   # Add it back in (G_without should be getting smaller)
            rewards['DIFFERENCE'][my_rover_index] = rewards['GLOBAL'] - G_without # Calculate D = G(Z) - G(Z_-i)

        # print rewards['DIFFERENCE']
        # print 'Any DIFFERENCE rewards less than zero?', any([el < 0 for el in rewards['DIFFERENCE']])
            
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


    def find_closest(self, poi_index, not_these_rovers=[]):
        """ Finds closest rover to the specified POI. 
        Returns that rover's index as well as the distance metric. """
        poi = self.POIs[poi_index]
        delta_min = 100.0  # start arbitrarily high
        rover_closest = None
        step_closest = None
        for rover_index, rover in enumerate(self.rovers):

            # Check observation distances for the rover locations we aren't skipping
            if rover_index not in not_these_rovers:
                for step_index, location in enumerate(self.rovers[rover_index].location_history):
                    delta = (location - poi)  # observation distance
                    if delta < delta_min:  # the closest rover counts, even if it's closer than the minimum observation distance
                        delta_min = delta
                        rover_closest = (rover_index, step_index)

        delta_min = max(delta_min ** 2, poi.d_min ** 2)  # delta is actually the SQUARED Euclidean distance
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

    def plot_all(self, rover_closest_list=[]):
        pyplot.ion()
    
        # Which step are we at?
        step = str(len(self.rovers[0].location_history))
        if int(step) < 10:
            step = '0' + step
        
        # Get the rewards thus far.
        rewards, rover_closest_list = self.get_rewards()

        # Plot each rover's trajectory, one by one
        pyplot.cla()  # clear axis
        pyplot.title('Step #' + str(step) + ', System Reward = ' + str(rewards['GLOBAL']))
        for this_rover_index, rover in enumerate(self.rovers):

            # Plot the world
            fig = pyplot.gcf()
            pyplot.axis([self.world_bounds.x_lower, self.world_bounds.x_upper, 
                         self.world_bounds.y_lower, self.world_bounds.y_upper])

            # Plot rovers
            trajectory_x = [point.x for point in rover.location_history]
            trajectory_y = [point.y for point in rover.location_history]
            pyplot.plot(trajectory_x, trajectory_y, 'r.-')
            pyplot.plot(trajectory_x[-1], trajectory_y[-1], 'ro')

            for poi_index, poi in enumerate(self.POIs):
                pyplot.plot(poi.location.x, poi.location.y, 'k*')

                # Check if a rover has been within the minimum observation distance of this POI
                delta_min, rover_closest = self.find_closest(poi_index)
                if delta_min < 1.05 * (poi.d_min ** 2):  # if within 5% of min. obs. distance (since an == relation might fail due to float math)
                    color_choice = 'g'
                else: 
                    color_choice = '0.5'  # lightish gray

                circle1 = pyplot.Circle((poi.location.x, poi.location.y), 5, color=color_choice, fill=False)
                fig.gca().add_artist(circle1)

        pyplot.draw()
        fig.savefig('Learned01Step' + str(step) + '.png')

