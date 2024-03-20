"""
The "brains" of the bot, where the decision-making will be made
Every decisionMaker is a child class od DecisionMaker and must implement the abstract methods.
"""

import math
from abc import abstractmethod

from config import positionSimConfig, knnConfig
from tradingClasses import Position


class DecisionMaker:
	@abstractmethod
	def getPosition(self, currentKlines, currentKlineIndex):
		"""
		Returns the best calculated position given the inputs

		:return:
		"""


def sma(klines, index, interval, klineValue="close"):
	"""
	Returns the sma of the kline at the index "index"

	:param klines: 		series of klines to calculate the sma on
	:param index: 		index of the kline the sma is wanted
	:param interval: 	interval of the sma
	:param klineValue: 	which kline value to consider (default: close)
	:return: 			returns a float that is the sma of that kline
	"""

	# exclude the first klines since we can't know the sma5
	if index < interval - 1:
		return None

	# calculate the sma
	sma = 0
	for j in range(interval):
		sma += klines[index - j][klineValue]

	sma /= interval

	return sma


def euclideanDistance(a, b):
	"""
	Returns the Euclidean distance of the two given points.

	:param a:
	:param b:
	:return:
	"""

	if len(a) != len(b):
		raise Exception("The two points must have the same length")

	dist = 0

	for i in range(len(a)):
		dist += (a[i] - b[i]) ** 2

	return math.sqrt(dist)


class Knn(DecisionMaker):
	def __init__(self, trainKlines: list, knnParams=knnConfig, positionParams=positionSimConfig):
		"""
		:param trainKlines:
		:param positionParams: the parameters of the simulated positions
			"sl": stop loss of the position
			"tp": take profit of the position
			"maxLength": the maximum number of klines to conclude the position
				MaxLength is used so the position does not get approval
				if it gets filled in like 21386 days from when it was placed.
			"minLength": the minimum number of klines to conclude the position
				MinLength is used so the position does not get approval
				if it gets filled in like 0 seconds from when it was placed.
				This is it avoid sudden spikes and uncertainty.
				Anyhow, the default for this should be low (1-3), especially when using
				small tp/sl
			"max chop": the maximum allowed chop in the position
				I don't actually know if I'll use this (it may be useless)
				The idea behind this is to avoid the price to fluctuate while we are in a position.
				If we want to use the results of a position as a prediction, it has to be as clean as possible.
				This of course would limit the number of positions, but maybe the profit factor would increase.
		"""

		self.trainKlines = trainKlines
		self.trainDataPoints = self.extractDataPoints(self.trainKlines)

		self.knnParams = knnParams

		self.positionParams = positionParams

	def getPosition(self, currentKlines, currentKlineIndex):
		"""
		Returns a dict containing both the predicted consideredPos and the considered consideredPos

		:param currentKlineIndex:	index of the wanted kline in the simulation klines
		:param currentKlines: 		list of simulation klines
		:return: 					{"predicted": position, "considered": []}
		"""

		# convert the currentKlines to dataPoints
		currentDataPoints = self.extractDataPoints(currentKlines)

		# get the knn for the last kline
		knn = self.getKnn(currentDataPoints[currentKlineIndex])

		if not knn:
			# the knn list is empty
			# (probably because the dp cant be calculated yet)
			print("the knn list is empty")
			return {"predicted": None, "considered": None}

		# check if the nn are acceptable
		meanDist = sum([nn["distance"] for nn in knn]) / len(knn)  # mean distance
		# bestDist = knn[0]["distance"]  # least distance
		# worstDist = knn[-1]["distance"]  # worst distance

		if meanDist > self.knnParams["threshold"]:
			# nn was not acceptable
			print(f"nn was not acceptable ({meanDist:.5f}/{knnConfig['threshold']})")
			return {"predicted": None, "considered": None}

		# for each nn simulate the position
		consideredPos = []
		for nn in knn:
			pos = self.simulatePosition(nn)
			if pos is not None:
				consideredPos.append(pos)

		# check the general direction of the positions and if it's good enough
		longPosCount = 0
		shortPosCount = 0

		for pos in consideredPos:
			if pos.direction == "long":
				longPosCount += 1

			elif pos.direction == "short":
				shortPosCount += 1

			else:
				raise Exception("How tf does this happen? The position is neither long nor short")

		if longPosCount > shortPosCount:
			ratio = longPosCount / (longPosCount + shortPosCount)
			direction = "long"
		elif longPosCount < shortPosCount:
			ratio = shortPosCount / (longPosCount + shortPosCount)
			direction = "short"
		else:
			return {"predicted": None, "considered": consideredPos}

		if ratio > knnConfig["sameDirectionRatio"]:
			print("Got a position!")
			predictedPos = Position(
				entryIndex=currentKlineIndex + 1, 	# +1 because
				exitIndex=None, 					# we don't know
				entryPrice=currentKlines[currentKlineIndex + 1]["open"],
				direction=direction,
				sl=positionSimConfig["sl"],
				tp=positionSimConfig["tp"],
				exitPrice=None,
				profit=None
			)
		else:
			print("Ratio was shit")
			predictedPos = None

		return {"predicted": predictedPos, "considered": consideredPos}

	@staticmethod
	def extractDataPoints(klines):
		"""
		Extract the necessary data points from the klines
		place them in a 2D list

		The problem here is that the data points have to be linked with their corresponding kline
		This will be problematic since a data point can be influenced by multiple klines
		I think I will fix this by assigning exactly one dataPoint to each kline.
		If a kline's dataPoint can't be calculated, the dataPoint will be None

		What's the meaning of a kline's dataPoint?
		A kline's dataPoint is basically extra info about that kline. Instead of having just ohlcv data, we can add
		indicators, mathematical functions etc. This data point will be used to compare the kline to other klines.
		Since we know the index of the dataPoint, we know also the index of the associated kline and thus also of
		the next kline (the prediction).

		possible dataPoints:
			1) Price change
				Simply the difference of the close and open price.
				It is basically a value that tells how big is a candle.
				Can be normalised by setting a max candle height (the huge candles will not
				be considered - they are an anomaly).
			2) Sma/ema slope
				The difference between the current sma/ema point and the previous one.
				Maybe can be calculated as the difference of the sma/ema of close values - sma/ema of open values.
					Seems that it works this way indeed
				Can be normalised by setting a max sma/ema slope (the steep candles will not
				be considered - they are an anomaly).
				IMPORTANT: here instead of calculating the slope, I subtract the open and close sma,
				like in price change. It is not exactly the same, but it gets the job done without another loop
			3) Boolean indicators (s&r, idk yet):
				Boolean indicators have to be normalised too. In a range [1, -1], the two boolean values would be
				1 and -1. This means that whatever normalisation we choose, the boolean values will be at the
				extremes of it.
				This means that we shouldn't use any data values that can go to infinity as it will fuck up all the
				nice normalisation that we want.

		:return:
		"""

		smaInterval = 5
		dataPoints = []

		for i in range(len(klines)):
			kline = klines[i]

			smaOpen = sma(klines, i, smaInterval, "open")
			smaClose = sma(klines, i, smaInterval, "close")

			try:
				smaDiff = smaClose - smaOpen
			except TypeError:
				# the sma is None since there is not enough data
				smaDiff = None

			dp = [
				kline["close"] - kline["open"], 	# price change
				smaDiff,  							# sma change
			]

			dataPoints.append(dp)

		return dataPoints

	def getKnn(self, dataPoint):
		"""
		Returns the k nearest neighbours of the given dataPoint
		The return is a json containing the data:
		[{"distance": distance, "index": index}, ...]

		:param dataPoint:
		:return:
		"""

		knn = []

		# compare distances with each dataPoint in the training dataset
		for index in range(len(self.trainDataPoints)):
			trainDp = self.trainDataPoints[index]

			try:
				distance = euclideanDistance(trainDp, dataPoint)
			except TypeError:
				# the dp is not calculated yet
				continue

			neighbour = {"distance": distance, "index": index}

			# if the list is still empty, just append the neighbour
			if len(knn) < self.knnParams["k"]:
				knn.append(neighbour)
				continue

			# sort the neighbours (for easier access)
			# lower distance first, higher at the end
			knn = sorted(knn, key=lambda x: x["distance"])

			# replace the worst neighbour with the better one
			if distance < knn[-1]["distance"]:
				knn[-1] = neighbour

		return knn

	def simulatePosition(self, nn):
		"""
		Simulates the position of the given nearest neighbour.
		It places a long position on the close price of index of nn.
		If the position is "good" (it's not inconclusive) and it makes profit, this will return a long position.
		But if it's conclusive, and it doesn't make profit it returns a short position.
		If the position is inconclusive, it will return None.

		:param nn:
		:return:
		"""

		posOpenIndex: int = nn["index"]
		entryPrice = self.trainKlines[posOpenIndex]["close"]

		# we assume that we are making a long position (doesn't matter anyway)
		tp = entryPrice + (entryPrice / 100) * self.positionParams["tp"]
		sl = entryPrice - (entryPrice / 100) * self.positionParams["sl"]

		# loop through every kline after the position opening and check if it hits the sl or tp
		for posCurrIndex in range(1, self.positionParams["maxLength"]):
			klinesIndex = posCurrIndex + posOpenIndex

			try:
				currentLow = self.trainKlines[klinesIndex]["low"]
				currentHigh = self.trainKlines[klinesIndex]["high"]
			except IndexError:
				# reached the end of the chart
				return None

			# if both high and low go over the tp/sl, then it's inconclusive
			if currentLow < sl and currentHigh > tp:
				print("tp and sl bot got hit")
				return None

			# The position should have been short
			# FIXME THIS IS SHIT. IF SL IS 0.1 AND TP IS 0.3 THEN ITS NOT THAT EASY
			# FIXME i guess i should only count the tp both up and down
			if currentLow < sl:
				return Position(
					entryIndex=posOpenIndex,
					exitIndex=klinesIndex,
					direction="short",
					entryPrice=entryPrice,
					exitPrice=sl,
					profit=None,
					sl=self.positionParams["tp"],  # yes, they are not inverted
					tp=self.positionParams["sl"]
				)

			# The position is correct (long)
			if currentHigh > tp:
				return Position(
					entryIndex=posOpenIndex,
					exitIndex=klinesIndex,
					direction="long",
					entryPrice=entryPrice,
					exitPrice=tp,
					profit=None,
					sl=self.positionParams["sl"],
					tp=self.positionParams["tp"]
				)

		# if nothing happens, the position is too long (inconclusive)
		# print(f"position is too long")
		return None
