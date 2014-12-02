#!/usr/bin/env python

# locationOfFiles = os.getcwd() + '/classes'  # add location of class files to PYTHONPATH
# print 'File loc: ', locationOfFiles
# sys.path.append(locationOfFiles)

import os
from matplotlib import pyplot, rc
import itertools
import sys


def figureItOut(x_lists, y_lists, axis_bounds):
    colors = 'kbrg'
    shapes = ['', '*', 'o', 's']
    lines = [':', '-', '-', '-']
    labels = ['Random Actions', 
              'Learning with 360$^\circ$ Sensor FoV', 
              'Learning with 270$^\circ$ Sensor FoV', 
              'Learning with 900$^\circ$ Sensor FoV']
    for x, y, color, shape, line, label in itertools.izip(x_lists, y_lists, colors, shapes, lines, labels):
        pyplot.plot(x, y,color+line+shape, label=label, markersize=8)
    pyplot.axis(axis_bounds)
    pyplot.xlabel('Number of Rovers')
    pyplot.ylabel('System Reward Per Rover after Learning')
    pyplot.title('Effect of Sensor Field-of-View on Learned Performance')
    pyplot.xticks([1, 2, 3], [3, 10, 100])  # make the evenly-spaced ticks refer to unevenly-spaced values
    pyplot.legend(loc='upper right')
    pyplot.show()

# tweaks to show sys rewards for 30 agents....
def figureItOutUpdated(x_lists, title_lists, axis_bounds, main_title = 'System Rewards'):
    colors = 'kbrg'
    shapes = ['', '*', 'o', 's']
    lines = [':', '-', '-', '-']
    labels = title_lists
    for x, color, shape, line, label in itertools.izip(x_lists, colors, shapes, lines, labels):
        pyplot.plot(x,color+line+shape, label=label, markersize=8)
    # pyplot.axis(axis_bounds)
    pyplot.xlabel('Number of Episodes')
    pyplot.ylabel('System Reward Per Rover after Learning')
    pyplot.title(main_title)
    # pyplot.xticks([1, 2, 3], [3, 10, 100])  # make the evenly-spaced ticks refer to unevenly-spaced values
    pyplot.legend(loc='upper right')
    pyplot.show()

def plotRewards(rewards, directory):
#     # 
#     # for filename in os.listdir('dirname'):
#     #      callthecommandhere(blablahbla, filename, foo)
#     # 
#     # font = {'family' : 'normal',
#  #            'weight' : 'bold',
#  #            'size'   : 16}

#  #    rc('font', **font)
    print 'in plot rewards...'
    pyplot.plot(rewards)
    pyplot.title(directory)
    pyplot.show()
#     # x_lists = [[1, 2, 3]]*4
#     # x_lists[0] = [0, 4]
#     # y_lists = [[26, 26],    # the baseline; gets treated differently
#     #            [180, 150, 142],
#     #            [131, 132, 131],
#     #            [99, 125, 112]]

#     # axis_bounds = [0.5, 3.5, 0, 300]
#     # figureItOut(x_lists, y_lists, axis_bounds)

def readInRewards(fname):
    rewards = []
    with open(fname, 'r') as f:
        for line in f:
            rewards.append(float(line))

        f.close()

    return rewards

def statRunsDirAvg(directory):
    ''' Averages all the float list files in the directory into one
    '''
    print 'Working on filepath..' + directory
    # Get each reward list from the directory
    rewardList = []
    for fname in os.listdir(directory):
        fnamePath = directory + '/' + fname
        print 'Filepath: ', fnamePath
        try:
            rewards = readInRewards(fnamePath)
            print 'Got rewards'
            rewardList.append(rewards)
        except:
            print "Cant get rewards..."
        
    # # average each list accross each row
    averageRewardList = getAverage(rewardList)

    # # save the list :)
    saveReward(directory, averageRewardList)

    # plot list
    # plotRewards(averageRewardList, directory)    


def getAverage(allRewardsList):
    ''' Computes the average reward for each cell in the same
        length reward list.
    '''
    
    averageRewardList = []
    for i in range(len(allRewardsList[0])):

        sumCell = 0
        for rewardList in allRewardsList:
            sumCell += rewardList[i]

        averageForCell = sumCell / len(allRewardsList)
        averageRewardList.append(averageForCell)

    return averageRewardList


def saveReward(fname, rewardList):
    fname = fname + 'AVG'

    d = os.path.dirname(fname)
    if not os.path.exists(d):
        os.makedirs(d)

    with open(fname, 'w') as f:
        for reward in rewardList:
            f.write(str(reward) + '\n')
        
        f.close()

def averageStatRuns():
    directory = '/nfs/attic/smartw/users/kraftko/Fall2014/ME538MultiAgent/TermProj/multiple-explorers/presentResults/'
    # for directory in os.listdir(os.getcwd + '/results/'):
    for direct in os.listdir(directory):
        newDirect = directory + str(direct) + '/'
        print newDirect
        print
        try:
            for subDir in os.listdir(str(newDirect)):
                filePath = '{0}/{1}/{2}'.format(directory, direct, subDir)
                # print '   SubDir: ', subDir
                # print  '     filepath: ', filePath
                statRunsDirAvg(filePath)
        except:
            pass

def plotGroup(fileNames, titleNames, mainTitle):
    directory = '/nfs/attic/smartw/users/kraftko/Fall2014/ME538MultiAgent/TermProj/multiple-explorers/presentResults/'

    # get rewards for each file
    rewardListTotal = []
    for fName in fileNames:
        fPath = directory + fName
        rewardList = readInRewards(fPath)
        rewardListTotal.append(rewardList)
        print 'Got rewards for: ', fPath

    # plot the rewards
    axisBounds = [0,100, 10000,20000]
    # def figureItOutUpdated(x_lists, title_lists, axis_bounds, main_title = 'System Rewards'):
    figureItOutUpdated(rewardListTotal, titleNames, axisBounds, mainTitle)



if __name__ == '__main__':
    # averageStatRuns()
    
    fileNames = []
    for i in range(1, len(sys.argv)):
        if sys.argv[i] == '-AVG':
            print 'Averaging each run type..'
            averageStatRuns()
            sys.exit(0)
        else:
            fileNames.append(sys.argv[i])

    titleNames = []
    # print len(fileNames)
    for fName in fileNames:
        tName = raw_input('Title for ' + fName + ' ...   ')
        titleNames.append(tName)

    mainTitle = raw_input('Main title?...  ')

    plotGroup(fileNames, titleNames, mainTitle)

    

    
    

   