#!/usr/bin/env python
# does my comment and committ work?
class World():
    pass


class POI():
    pass


import math

class Location:
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
            """ Location subtraction = Euclidean distance between the two. """
            return math.sqrt((self.x - subtrahend.x) ** 2 + (self.y - subtrahend.y) ** 2)

