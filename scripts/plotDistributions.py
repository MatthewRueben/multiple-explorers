#!/usr/bin/env python

import os, sys
locationOfFiles = os.getcwd() + '/classes'  # add location of class files to PYTHONPATH
print 'File loc: ', locationOfFiles
sys.path.append(locationOfFiles)

import numpy
import matplotlib
from matplotlib import pyplot, image
from geography import POI, Bounds2D, Location
from rovers import Rover
import random

def main(distro='GO_RANDO!'):
    
    # World parameters
    N_POIs = 100
    world_bounds = Bounds2D((0, 115), (0, 100))  # world borders
    world_center = Location(60, 50)  # where the agents start at
    poi_ranges = (70, 70)
    poi_bounds = Bounds2D((world_center.x-poi_ranges[0]/2, world_center.x+poi_ranges[0]/2), 
                          (world_center.y-poi_ranges[1]/2, world_center.y+poi_ranges[1]/2))  # bounds of where POIs can go

    # Axis params
    fig = pyplot.gcf()
    pyplot.axis([world_bounds.x_lower, world_bounds.x_upper, 
                 world_bounds.y_lower, world_bounds.y_upper])

    # Make POIs
    POIs = []
    if distro == 'GO_RANDO!':  # random
        for i in range(N_POIs):
            poi = POI(V=10, d_min=5)
            poi.place_randomly(poi_bounds)
            POIs.append(poi)
    if distro == 'CLUMPISH':  # clump-ed
        corner_bounds = Bounds2D((world_center.x-poi_ranges[0]/2, world_center.x-poi_ranges[0]/2+15), 
                                 (world_center.y, world_center.y+poi_ranges[1]/2))
        corner_bounds2 = Bounds2D((world_center.x, world_center.x+poi_ranges[0]/2), 
                                 (world_center.y-poi_ranges[1]/2, world_center.y-poi_ranges[1]/2+15))
        N_corner = 20
        V_cap = 1000  # same total reward
        V_picks = []
        for i in range(N_corner):  # pick POI values beforehand
            V_pick = random.uniform(1, V_cap)
            V_picks.append(V_pick)
        V_sum = sum(V_picks)
        V_picks = [V_pick/V_sum*V_cap for V_pick in V_picks]  # normalize to 1000 total points
        for i, V_pick in zip(range(N_corner), V_picks):  # one-tenth the POIs
            poi = POI(V=V_pick, d_min=5)
            if V_pick > V_cap/2: 
                poi.place_randomly(corner_bounds)
            else:
                poi.place_randomly(corner_bounds2)
            POIs.append(poi)

    # Calculate sensor values
    print 'Some call me.........................Tim.'

    x_size = world_bounds.x_upper - world_bounds.x_lower
    y_size = world_bounds.y_upper - world_bounds.y_lower
    headings_size = 360 
    headings_list = range(0, headings_size, 5)
    amplitudes = numpy.zeros([y_size, x_size, len(headings_list)])
    for heading_pick_index, heading_pick in enumerate(headings_list):
        print heading_pick
        outputs_one_heading = numpy.zeros([y_size, x_size])
        for x_pick in range(world_bounds.x_lower, world_bounds.x_upper):
            for y_pick in range(world_bounds.y_lower, world_bounds.y_upper):
                rover = Rover('Tim', x=x_pick, y=y_pick, heading=heading_pick, num_sensors=4, 
                              observation_range=5.0, sensor_range=1000.0, sensor_noise=0.0, 
                              num_POI=100)
                #print rover.location
                inputs = rover.getNNInputs(POI_list=POIs, min_observation_dist=5.0, rover_list=[])
                front_sensor_input = inputs[0]
                #print front_sensor_input
                outputs_one_heading[y_pick, x_pick] = front_sensor_input
        gradients_x, gradients_y = numpy.gradient(outputs_one_heading)
        amplitudes[:, :, heading_pick_index] = numpy.sqrt(gradients_x**2 + gradients_y**2)
    amplitude = numpy.mean(amplitudes, axis=2)

    # Plot 'em
    for poi in POIs:
        #pyplot.plot(poi.location.x, poi.location.y, 'k*')
        color_choice = 'g'
        #circle_outer = pyplot.Circle((poi.location.x, poi.location.y), 5.0, color=color_choice, fill=False)
        #circle_inner = pyplot.Circle((poi.location.x, poi.location.y), 10.0*poi.V/1000, color=color_choice, fill=False)
        pyplot.plot(poi.location.x, poi.location.y, color='g', marker='*', markersize=14)
        #fig.gca().add_artist(circle_outer)
        #fig.gca().add_artist(circle_inner)

    pyplot.imshow(amplitude)
    pyplot.set_cmap('gray')
    pyplot.clim(0, 1.0)
    #pyplot.colorbar()
    pyplot.xlabel('X')
    pyplot.ylabel('Y')
    matplotlib.rcParams.update({'font.size': 20})
    pyplot.show()


if __name__ == '__main__':
    main('CLUMPISH')
    main('GO_RANDO!')
   
