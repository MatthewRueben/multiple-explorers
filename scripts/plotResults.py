#!/usr/bin/env python

# locationOfFiles = os.getcwd() + '/classes'  # add location of class files to PYTHONPATH
# print 'File loc: ', locationOfFiles
# sys.path.append(locationOfFiles)

import os
from matplotlib import pyplot, rc
import itertools


def figureItOut(x_lists, y_lists, axis_bounds):
    # colors = 'kbrg'
    # shapes = ['', '*', 'o', 's']
    # lines = [':', '-', '-', '-']
    # labels = ['Random Actions', 
    #           'Learning with 360$^\circ$ Sensor FoV', 
    #           'Learning with 270$^\circ$ Sensor FoV', 
    #           'Learning with 900$^\circ$ Sensor FoV']
    # for x, y, color, shape, line, label in itertools.izip(x_lists, y_lists, colors, shapes, lines, labels):
    #     pyplot.plot(x, y,color+line+shape, label=label, markersize=8)
    # pyplot.axis(axis_bounds)
    # pyplot.xlabel('Number of Rovers')
    # pyplot.ylabel('System Reward Per Rover after Learning')
    # pyplot.title('Effect of Sensor Field-of-View on Learned Performance')
    # pyplot.xticks([1, 2, 3], [3, 10, 100])  # make the evenly-spaced ticks refer to unevenly-spaced values
    # pyplot.legend(loc='upper right')
    pyplot.show()

def plotRewards(rewards):
	# 
	# for filename in os.listdir('dirname'):
	#      callthecommandhere(blablahbla, filename, foo)
	# 
	font = {'family' : 'normal',
            'weight' : 'bold',
            'size'   : 16}

    rc('font', **font)

    pyplot.plot(rewards)
    pyplot.show()

    # x_lists = [[1, 2, 3]]*4
    # x_lists[0] = [0, 4]
    # y_lists = [[26, 26],    # the baseline; gets treated differently
    #            [180, 150, 142],
    #            [131, 132, 131],
    #            [99, 125, 112]]

    # axis_bounds = [0.5, 3.5, 0, 300]
    # figureItOut(x_lists, y_lists, axis_bounds)

def getRewards(fname):
	rewards = []
	with open(fname, 'r') as f:
		for line in f:
			rewards.append(float(line))

		f.close()

	return rewards

def main(directory):

	for fname in os.listdir(directory):
		rewards = getRewards(fname)
		plotRewards(rewards)


if __name__ == '__main__':
	
	for directory in os.listdir(os.getcwd + '/results/')
		main(directory)


    
    

   