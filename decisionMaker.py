from abc import ABC, abstractmethod


class DecisionMaker:
	@abstractmethod
	def getPosition(self, currentKlines):
		"""
		Returns the best calculated position given the inputs

		:return:
		"""

	@abstractmethod
	def getNextKline(self):
		"""
		Returns the next calculated kline

		:return:
		"""


class Knn(DecisionMaker):
	def __init__(self, trainKlines):
		self.trainKlines = trainKlines
		self.dataPoints = self.extractDataPoints()

	def getPosition(self, inputs):
		pass
	
	def getNextKline(self):
		pass

	def extractDataPoints(self):
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
			3) Boolean indicators (s&r, idk yet):
				Boolean indicators have to be normalised too. In a range [1, -1], the two boolean values would be
				1 and -1. This means that whatever normalisation we choose, the boolean values will be at the
				extremes of it.
				This means that we shouldn't use any data values that can go to infinity as it will fuck up all the
				nice normalisation that we want.

		:return:
		"""

		dataPoints = []

		smaInterval = 5

		for i in range(len(self.trainKlines)):
			# exclude the first klines since we can't know the sma5
			if i < smaInterval:
				dataPoints.append(None)
				continue

			# calculate the sma
			closeSma = 0
			openSma = 0
			for j in range(smaInterval):
				closeSma += self.trainKlines[i - j]["close"]
				openSma += self.trainKlines[i - j]["open"]

			closeSma /= smaInterval
			openSma /= smaInterval

			smaDiff = closeSma - openSma

			kline = self.trainKlines[i]

			dataPoints.append(
				[
					kline["close"] - kline["open"],		# price change
					smaDiff								# sma5 change
				]
			)

		return dataPoints
