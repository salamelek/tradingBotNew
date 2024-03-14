"""
The classes that are used primarily for plotting and displaying info.
"""

from matplotlib.collections import PatchCollection
from matplotlib.patches import Rectangle

from config import positionSimConfig


class Chart:
    def __init__(self, klines: list, indicators=(), positions=(), plotIndicators=True, plotPositions=True):
        self.klines = klines
        self.indicators = indicators
        self.positions = positions

        self.hlWidth = 0.1
        self.lineHeight = 0.0001
        self.bullishColor = "green"
        self.bearishColor = "red"
        self.rangingColor = "yellow"

        self.plotIndicators = plotIndicators
        self.plotPositions = plotPositions

    def __str__(self):
        return f"""
CHART INFO

num of klines: {len(self.klines)}
some other info here maybe :>
"""

    def plot(self, axs):
        bullish = []
        bearish = []
        ranging = []

        for index in range(len(self.klines)):
            kline = self.klines[index]

            coords = (index - 0.5, kline["open"])  # (index, openPrice)
            width = 1  # 1, because each index is large 1
            height = kline["close"] - kline["open"]  # closePrice - openPrice

            coordsHl = (((index + 0.5) - self.hlWidth / 2) - 0.5, kline["low"])
            heightHl = kline["high"] - kline["low"]

            if height > 0:
                bullish.append(Rectangle(coords, width, height))
                bullish.append(Rectangle(coordsHl, self.hlWidth, heightHl))
            elif height < 0:
                bearish.append(Rectangle(coords, width, height))
                bearish.append(Rectangle(coordsHl, self.hlWidth, heightHl))
            else:
                ranging.append(Rectangle(coords, width, self.lineHeight))

        axs[0].add_collection(PatchCollection(bullish, edgecolor="none", facecolor=self.bullishColor))
        axs[0].add_collection(PatchCollection(bearish, edgecolor="none", facecolor=self.bearishColor))
        axs[0].add_collection(PatchCollection(ranging, edgecolor="none", facecolor=self.rangingColor))

        # plot volume
        axs[1].plot(range(len(self.klines)), [kline["volume"] for kline in self.klines])

        # plot indicators
        if self.plotIndicators:
            for indicator in self.indicators:
                indicator.plot(axs)

        # plot positions
        if self.plotPositions:
            for position in self.positions:
                if position is None:
                    continue

                position.plot(axs)

        axs[0].errorbar(0, 1)


class Indicator:
    def __init__(self):
        pass

    def __str__(self):
        pass

    def plot(self, axs):
        pass


class Position:
    def __init__(self, entryIndex, exitIndex, entryPrice, direction, sl, tp, exitPrice, profit):
        self.entryIndex = entryIndex
        self.exitIndex = exitIndex
        self.entryPrice = entryPrice
        self.direction = direction
        self.sl = sl
        self.tp = tp
        self.exitPrice = exitPrice
        self.profit = profit

    def __str__(self):
        return (f"{self.direction} position at index {self.entryIndex}\n"
                f"\tEntry price: {self.entryPrice}\n\tExit price: {self.exitPrice}")

    def plot(self, axs):
        positionSquareOpacity = 0.2

        width = positionSimConfig["maxLength"]
        origin = (self.entryIndex, self.entryPrice)

        greenRects = []
        redRects = []

        print(self)

        if self.direction == "long":
            upperPrice = self.entryPrice + (self.entryPrice / 100) * self.tp
            lowerPrice = self.entryPrice - (self.entryPrice / 100) * self.sl

            upperLimit = upperPrice - self.entryPrice
            lowerLimit = lowerPrice - self.entryPrice

            greenRects.append(Rectangle(origin, width, upperLimit))
            redRects.append(Rectangle(origin, width, lowerLimit))

        elif self.direction == "short":
            upperPrice = self.entryPrice + (self.entryPrice / 100) * self.sl
            lowerPrice = self.entryPrice - (self.entryPrice / 100) * self.tp

            upperLimit = upperPrice - self.entryPrice
            lowerLimit = lowerPrice - self.entryPrice

            greenRects.append(Rectangle(origin, width, lowerLimit))
            redRects.append(Rectangle(origin, width, upperLimit))

        else:
            raise Exception("Invalid direction")

        axs[0].add_collection(PatchCollection(greenRects, edgecolor="none", facecolor="green", alpha=positionSquareOpacity))
        axs[0].add_collection(PatchCollection(redRects, edgecolor="none", facecolor="red", alpha=positionSquareOpacity))

