import numpy as np
import time
from datetime import datetime
import random


	# X = (hours studying, hours sleeping), y = score on test, xPredicted = 4 hours studying & 8 hours sleeping (input data for prediction)
	#X = np.array(([2, 9], [1, 5], [3, 6], [5, 2]), dtype=float)
	#y = np.array(([11], [6], [9], [7]), dtype=float)
	#X,y = generateTrainingArithmatic();

	#for i in range(0,len(y)):
		#print(str(X[i]) + " = "  + str(y[i]));

	#xPredicted = np.array(([4, 3]), dtype=float)

	# scale units
	#XMax = np.amax(X, axis=0);
	#print(XMax);
	#X = X / XMax # maximum of X array
	#xPredicted = xPredicted / np.amax(
	#	xPredicted,
	#	axis=0)  # maximum of xPredicted (our input data for the prediction)
	#y = y / 100  # max test score is 100

	#f = open("predictions.csv","w");
	#NN = Neural_Network(xPredicted)
	#startTime = time.time();
	#for i in range(1000):  # trains the NN 1,000 times
	#	print(" #" + str(i));
	#	print("Input (scaled): \n" + str(X));
	#	print("Actual Output: \n" + str(y));
	#	print("Predicted Output: \n" + str(NN.forward(X)));
		#loss = str(np.mean(np.square(y-NN.forward(X))));
		#print("Loss: \n" + loss);  # mean sum squared loss
		#print("\n");
		#NN.train(X, y)
		#NN.saveWeights()

		#h,j = NN.predict()
		#if(i % 10 == 0):
	#		f.write(str(i) + "," + str(j[0]) + ";\n");
		
	#endTime = time.time();
	#print("Run Time: " + str(endTime - startTime) + " seconds");

class Neural_Network(object):
	def __init__(self, xPredicted):
		#parameters
		self.inputSize = 2
		self.outputSize = 1
		self.hiddenSize = 50 #1000
		self.xPredicted = xPredicted

		#weights
		self.W1 = np.random.randn(
				self.inputSize,
				self.hiddenSize)	# (3x2) weight matrix from input to hidden layer
		self.W2 = np.random.randn(
				self.hiddenSize,
				self.outputSize)	# (3x1) weight matrix from hidden to output layer

	def forward(self, X):
		#forward propagation through our network
		#for i in range(0,len(X)):
		#	print(X[i]);
		#print(len(X[0]));
		#print(X[0]);
	
		#print(self.W1);
		self.z = np.dot( X, self.W1)	# dot product of X (input) and first set of 3x2 weights
		self.z2 = self.sigmoid(self.z)	# activation function
		self.z3 = np.dot( self.z2, self.W2)  # dot product of hidden layer (z2) and second set of 3x1 weights
		o = self.sigmoid(self.z3)  # final activation function
		return o

	def sigmoid(self, s):
		# activation function
		return 1 / (1 + np.exp(-s))

	def sigmoidPrime(self, s):
		#derivative of sigmoid
		return s * (1 - s)

	def backward(self, X, y, o):
		# backward propgate through the network
		self.o_error = y - o	# error in output
		self.o_delta = self.o_error * self.sigmoidPrime(o)	# applying derivative of sigmoid to error

		self.z2_error = self.o_delta.dot(
				self.W2.T
		)  # z2 error: how much our hidden layer weights contributed to output error
		self.z2_delta = self.z2_error * self.sigmoidPrime(
				self.z2)	# applying derivative of sigmoid to z2 error

		self.W1 += X.T.dot(
				self.z2_delta)	# adjusting first set (input --> hidden) weights
		self.W2 += self.z2.T.dot(
				self.o_delta)  # adjusting second set (hidden --> output) weights

	def train(self, X, y):
		o = self.forward(X)
		self.backward(X, y, o)

	def saveWeights(self):
		np.savetxt("w1.txt", self.W1, fmt="%s")
		np.savetxt("w2.txt", self.W2, fmt="%s")

	def predict(self):
		print("Predicted data based on trained weights: ")
		before = self.xPredicted;
		print("Input (scaled): \n" + str(self.xPredicted))
		print("Output: \n" + str(self.forward(self.xPredicted)))
		after = self.forward(self.xPredicted);
		return before, after;
main();
