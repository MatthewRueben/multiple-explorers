#!/usr/bin/env python
# Tests the classes in .../classes/Environment.py

import sys
sys.path.append('/nfs/attic/smartw/users/ruebenm/workspaces/exploration/src/classes')  # add location of class files to PYTHONPATH

from environment import Location, Bounds2D, World
import random

if __name__ == "__main__":

    # Test Location class
    a = Location(x=1, y=-3)
    b = Location(x=-1, y=1)
    c = Location(x=-1, y=1)
    print a
    print 'Should be 4.47:', a - b
    print 'Should be True:', b == c

    # Test World class (and POI, 2DBounds classes by extension)
    world_bounds = Bounds2D((0, 115), (0, 100))
    world_center = Location(60, 50)
    poi_ranges = (70, 70)
    poi_bounds = Bounds2D((world_center.x-poi_ranges[0]/2, world_center.x+poi_ranges[0]/2), 
                          (world_center.y-poi_ranges[1]/2, world_center.y+poi_ranges[1]/2))
    print 'Should be ((25, 95), (15, 85)):', poi_bounds
    world = World(world_bounds, 100, poi_bounds, 30, rover_start=world_center)  # make a world
    world.reset()  # randomize POI locations and reset rover locations
    for time_step in range(15):  # for 15 time steps...
        for rover in world.rovers:  # move all the rovers
            dx = random.choose(range(-5,6))
            dy = random.choose(range(-5,6))
            rover.takeAction(dx, dy)
    rewards, rover_closest_list = world.get_rewards()
    print 'Rewards:', rewards
    world.test_plot(rover_closest_list)
    input('Press RETURN to quit. ')
