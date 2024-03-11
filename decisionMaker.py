from abc import ABC, abstractmethod


class DecisionMaker:
	@abstractmethod
	def getPosition(self, inputs):
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
	def getPosition(self, inputs):
		pass
	
	def getNextKline(self):
		pass
