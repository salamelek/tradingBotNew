from abc import ABC, abstractmethod


class DecisionMaker:
	@abstractmethod
	def getPosition(self, inputs):
		"""
		Returns the best calculated position given the inputs

		:return:
		"""


class JustAnExample(DecisionMaker):
	def getPosition(self, inputs):
		print("helo")
