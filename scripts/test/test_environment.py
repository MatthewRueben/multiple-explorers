#!/usr/bin/env python
# Tests the classes in .../classes/Environment.py

import sys
sys.path.append('/nfs/attic/smartw/users/ruebenm/workspaces/exploration/src/classes')  # add location of class files to PYTHONPATH

from environment import World, POI, Location

if __name__ == "__main__":
    # Test Location class
    a = Location(x=1, y=-3)
    b = Location(x=-1, y=1)
    c = Location(x=-1, y=1)
    print a
    print 'Should be 4.47:', a - b
    print 'Should be True:', b == c

    
               
