#!/usr/bin/env python

'''
Purpose:
Class to define FF, single hidden layer, neural network.
Specifically, the NN will be used with rover domain.


In Evo Part:
Mutate about 10% of weights.
1 way to modify (that works) take previous weight then add random sample for
    normal distribution
Don't forget bias term :)
  
@author Kory Kraft
@date 11/24/2014
'''

import math
import copy
import random
import sys

class NeuralNetwork():
	''' Creates a NN for a single layer FF NN 
		The activation function is the same for all the nodes
	'''
	def __init__(self, input, hiddenLayer, output, weights = {}, verbose = False):
		''' Expecting:
				The numpber of input nodes
				The numer of hidden layer nodes
				The number of output nodes

		'''
		self.numInputNodes = input
		self.numHiddenLayerNodes = hiddenLayer
		self.numOutputLayerNodes = output
		self.weights = weights

		# used to train the network using evo
		self.selected = False
		self.value = sys.float_info.min

		# for error checking
		self.verbose = verbose

	def supplyInputs(self, inputs):
		''' At this point, I am expecting a list for the inputs
			The NN doesn't care what order they are in at this point.

		'''
		self.poiInput = poiInput
		self.rovInput = rovInput

	def printWeights(self):
		output = 'Weights\n\n{0}'.format(self.weights)
		print output

	def __repr__(self):
		return self.__str__()

	def __str__(self):
		# return '\nNN: \nInput Nodes: {0}\nHidden Layer Nodes: {1}\nOutput Nodes: {2}\n\nWeights:\n{3}\nNum Weights: {4}'\
		# 		.format(self.numInputNodes, self.numHiddenLayerNodes, self.numOutputLayerNodes, self.weights, len(self.weights))
		return '\nNN: \nInput Nodes: {0}\nHidden Layer Nodes: {1}\nOutput Nodes: {2}\n\nWeights:\n{3}\nNum Weights: {4}'\
				.format(self.numInputNodes, self.numHiddenLayerNodes, self.numOutputLayerNodes, 'Not printing', len(self.weights))

	def activationFunction(self, x):
		''' Performs the activation function on x.
			Returns 0 or 1
			0 means not activated.
			1 means activated. 
			Currently uses the sigmoid function.
		'''
		activation = 1 / (1 + math.exp(-x))
		return activation

	def createNodes(self):
		''' Creates three equivalence classes of nodes:
				self.inputNodes (includes bias)
				self.hiddenNodes (includes bias)
				self.outputNodes 
			Naming convention is the following (keeping them in order helped sort the keys in the dictionary which made prediction easier)
						Input-IndexInt or Input-Bias
						Obscure-IndexInt or Obscure-Bias
						Output-IndexInt 
									
		'''
		self.inputNodes = ['Input-' + str(x) for x in xrange(self.numInputNodes)]
		self.inputNodes.append('Input-Bias')
		self.hiddenNodes = ['Obscure-' + str(x) for x in xrange(self.numHiddenLayerNodes)]
		self.hiddenNodes.append('Obscure-Bias')
		self.outputNodes = ['Output-' + str(x) for x in xrange(self.numOutputLayerNodes)]

	def createWeights(self):
		''' Creates a dictionary of weights between the input nodes + bias and hidden nodes as well as the 
				hidden nodes + bias and the output nodes.
			The keys are the the form of 'firstNodeName , secondNodeName'; (e.g. Input-5, Hidden-0)
			The weights are all initialized to .5
		'''
		if (self.weights == None):
			self.weights = {}

		# add weights between input nodes and hidden nodes
		for nodeI in self.inputNodes:
			for nodeH in self.hiddenNodes:
				if nodeH == 'Obscure-Bias':
					break # don't connect any inputs to the hidden bias....
				key = nodeI + ', ' + nodeH
				# print 'Key: ' + key
				self.weights[key] = .5

		# add weights between the hidden nodes and output nodes
		for nodeH in self.hiddenNodes:
			for nodeO in self.outputNodes:
				key = nodeH + ', ' + nodeO
				self.weights[key] = .5

		# print 'total weights: ', len(self.weights)

	def predict(self, inputs):
		''' Takes the list of inputs and predicts the number of outputs.
			List should map to number of inputs.
				For our specific rover domain lets have them in the order of 4 poi vals and 4 rov num vals.
				Our output will be 2 vals, dx and dy
		'''
		# # init an empty list of "inputs" for the hidden node corresponding to the index of the list
		# # don't need to include the bias for this hiddenNodeInput list...i think?
		# hiddenNodeInput = [0 for x in xrange(len(self.hiddenNodes) -1)] 
		# for key in sorted(self.weights.keys()):
		# 	print key
		# 	if 'Input' in key: 
		# 		# these are the "input" keys
		# 		# we can calculate the sum of each ones as it goes to the a given output?
		# 		node = key.split(',')[1].strip() # get the second named node, as it will be the one the init is attached to in the hidden layer
		# 		nodeIndex = int(node.split('-')[1].strip())
		# 		print 'Node:', node, 'Node Index:', nodeIndex
		# 		print 'Hidden node input: ', hiddenNodeInput
		# 		print 'Weight: ', self.weights[key]
		# 		print 'len of input', len(inputs)
		# 		print 'len of hiddenNodeInput, ', len(hiddenNodeInput)
		# 		hiddenNodeInput[nodeIndex] += self.weights[key] * inputs[nodeIndex]
		# 		print '  ', hiddenNodeInput[nodeIndex]
		
		# calculate the input for each node in the hidden layer
		# run the hidden node's input value through the activation function
		# Create a dictionary of key-value pairs, where the hidden nodes input index is the key 
		#   and the value is the activation function output
		
		hiddenNodeOutputs = {}
		for node in self.hiddenNodes:
			nodeName = node.split('-')[1].strip()
			if self.verbose:
				print 'Node name: ', nodeName
			# Bias term in hidden layer does not have inputs
			if nodeName != 'Bias':
				hiddenNodeInput = self.calculateNodeInput(nodeName, 'Obscure', inputs, 'Input') # with the way this is set up, this is an n2 operation :(
				value = self.activationFunction(hiddenNodeInput)
				hiddenNodeOutputs[nodeName] = value

		print 'Hidden Node Output Dictionary\n', hiddenNodeOutputs
		# sortedKeys = sorted(hiddenNodeOutputs.keys())
		# print sortedKeys
		hiddenNodeOutputList = [hiddenNodeOutputs[str(x)] for x in range(len(hiddenNodeOutputs))] 
		print hiddenNodeOutputList
		outputList = []
		for node in self.outputNodes:
			nodeName = node.split('-')[1].strip()
			if self.verbose:
				print 'Node name: ', nodeName
			hiddenNodeInput = self.calculateNodeInput(nodeName, 'Output', hiddenNodeOutputList, 'Hidden') # with the way this is set up, this is an n2 operation :(
			value = self.activationFunction(hiddenNodeInput)
			if self.verbose:
				print value
			outputList.append(value)

		return tuple(outputList)	


	def calculateNodeInput(self, nodeName, nodeType, inputs, inputType):
		''' Calculates the input for the node with the name "nodeName".
			nodeName is expected to be an integer.

			nodeType and inputType are currently only used for testing output.

			This method is by no means optimized as it goes through the entire list of keys in the node dictionary...
			Inputs are assumed to be mapped to output node
		'''
		# Goes through the sorted keys
		# Checks to see if the key/edge includes the hidden node name as the one which receives the input
		# if so, takes the weight of the edge and the current value associated with the input node and calculates an "increment"
		#   to add to the node's total sum
		total = 0
		counted = 0
		for key in sorted(self.weights.keys()):
			#if (', Obscure-' + nodeName) in key: 
			if (', ' + nodeType + '-' + nodeName) in key:
				#print key
				inputNode = key.split(',')[0].strip() # get the first named node as it goes to this particular input
				indexNodeTerm = inputNode.split('-')[1].strip()
				increment = 0
				if inputNode == 'Bias':
					inputIndex = 'Bias'
					increment = self.weights[key] * 1
				elif indexNodeTerm == 'Bias':
					inputIndex = 'Bias'
					increment = self.weights[key] * 1
				else:
					inputIndex = int(indexNodeTerm)
					increment = self.weights[key] * inputs[inputIndex]
				total += self.weights[key] * increment
				counted += 1
				if self.verbose:
					print '{0} node {1} connected to {2} {3}.     Adding: {4}'.format(inputType, inputIndex, nodeType, nodeName, increment)
		if self.verbose:
			print 'Total counted: ', counted
		return total	

	def getTotalNodes(self):
		return self.numInputNodes + self.numHiddenLayerNodes + self.numOutputLayerNodes

	def getTotalWeights(self):
		return len(self.weights)

	def changeWeight(self, key, newValue):
		''' Changes the weight for key to the newValue
		'''
		self.weights[key] = newValue

	def mutateWeights(self):
		''' Mutates a random 10% of the given weights by adding in
			some random number from a normalized distribution with mean of 0 and std deviation of 1.
			Returns a deep copy of the neural net with the mutated weights.
		'''
		# make a deep copy of the NN.
		mutatedNN = copy.deepcopy(self)
		# take a random sample of 10% of the keys
		keysToMutate = random.sample(self.weights.keys(), int(len(self.weights)/10))
		for key in keysToMutate:
			mutatedNN.weights[key] = self.weights[key] + random.gauss(0,1)


		return mutatedNN


def main():
	# init a "dummy" nn just to print to make sure setup is correct
	nn = NeuralNetwork(8, 10, 2)
	nn.createNodes()
	nn.createWeights()
	print nn
	print nn.predict([x for x in range(8)]) # inputs are just 0,1,2..7
	print 
	print 'Mutating....'
	mutatedNN = nn.mutateWeights()
	print mutatedNN
	print mutatedNN.predict([x for x in range(8)])
	print nn.predict([x for x in range(8)]) # inputs are just 0,1,2..7


	# NN for estimating x2 + 1 :)
	# nn = NeuralNetwork(1, 5, 1)
	# nn.createNodes()
	# nn.createWeights()
	# print nn
	# print nn.predict([x for x in range(1)]) # inputs are just 0,1,2..7
	# print 
	# print 'Mutating....'
	# mutatedNN = nn.mutateWeights()
	# print mutatedNN
	# print mutatedNN.predict([1])
	# print nn
	


if __name__ == '__main__':
	main()


