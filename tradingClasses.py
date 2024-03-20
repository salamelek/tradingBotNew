"""
The classes that are used primarily for plotting and displaying info.
"""

from matplotlib.collections import PatchCollection
from matplotlib.patches import Rectangle
import matplotlib.pyplot as plt

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
        if self.plotPositions and self.positions:
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
    def __init__(self, entryIndex, exitIndex, entryPrice, direction, sl, tp, exitPrice):
        self.entryIndex = entryIndex
        self.exitIndex = exitIndex
        self.entryPrice = entryPrice
        self.direction = direction
        self.sl = sl
        self.tp = tp
        self.exitPrice = exitPrice

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
            upperLimit = (self.entryPrice * self.tp) / 100
            lowerLimit = (self.entryPrice * self.sl) / -100

            greenRects.append(Rectangle(origin, width, upperLimit))
            redRects.append(Rectangle(origin, width, lowerLimit))

        elif self.direction == "short":
            upperLimit = (self.entryPrice * self.sl) / 100
            lowerLimit = (self.entryPrice * self.tp) / -100

            greenRects.append(Rectangle(origin, width, lowerLimit))
            redRects.append(Rectangle(origin, width, upperLimit))

        else:
            raise Exception("Invalid direction")

        axs[0].add_collection(
            PatchCollection(greenRects, edgecolor="none", facecolor="green", alpha=positionSquareOpacity))
        axs[0].add_collection(PatchCollection(redRects, edgecolor="none", facecolor="red", alpha=positionSquareOpacity))


class Backtest:
    # FIXME this whole class is shit, consider remaking everything

    def __init__(self, klines: list, decisionMaker, commissionFee=0.1, maxOpenPositions=1, positionSize=100):
        self.klines = klines
        self.decisionMaker = decisionMaker

        self.commissionFee = commissionFee
        self.maxOpenPositions = maxOpenPositions
        self.positionSize = positionSize

        self.stats = self.runBacktest()

    def __str__(self):
        return f"""
╔═╣ BACKTEST RESULTS:
║
║   Net profit:                 {self.stats["netProfit"]:.2f}€
║   Profit factor:              {self.stats["profitFactor"]:.2f}
╠════════════════════════════════════
║   Gross profit:               {self.stats["grossProfit"]:.2f}€
║   Gross loss:                 {self.stats["grossLoss"]:.2f}€
║   Max drawdown:               {self.stats["maxDrawdown"]:.2f}€
╠════════════════════════════════════
║   Num. of positions:          {len(self.stats["totPositions"])}
║   Num. of long positions:     {len(self.stats["longPositions"])}
║   Num. of short positions:    {len(self.stats["shortPositions"])}
╠════════════════════════════════════
║   Num. of winning positions:  {len(self.stats["winningPositions"])}
║   Num. of losing positions:   {len(self.stats["losingPositions"])}
╚════════════════════════════════════
        """

    def plot(self):
        """
        Plots the backtesting results
        :return:
        """

        print("Plotting...")

        chart = Chart(self.klines, positions=self.stats["totPositions"])

        fig = plt.figure()
        gs = fig.add_gridspec(2, 1, hspace=0, height_ratios=[4, 1])
        axs = gs.subplots(sharex=True)

        # plot chart (with indicators and positions)
        chart.plot(axs)

        for ax in axs:
            ax.label_outer()

        plt.tight_layout()

        axs[0].grid(True)
        axs[1].grid(True)
        # axs[0].legend()
        plt.show()

        print("Done!\n")

    def runBacktest(self):
        stats = {
            "longPositions": [],
            "shortPositions": [],
            "totPositions": [],
            "winningPositions": [],
            "losingPositions": [],
            "duration": 0,
            "profitFactor": 0,
            "maxDrawdown": 0,
            "grossProfit": 0,
            "grossLoss": 0,
            "commission": 0,
            "netProfit": 0,
            "percentProfitable": 0
        }

        # for each kline in backtest klines
        for i in range(len(self.klines)):
            predictedPos = self.decisionMaker.getPosition(self.klines, i)["predicted"]

            if not predictedPos:
                # skip None
                continue

            # set position's tp and sl
            if predictedPos.direction == "long":
                posTp = predictedPos.entryPrice + (predictedPos.entryPrice / 100) * predictedPos.tp
                posSl = predictedPos.entryPrice - (predictedPos.entryPrice / 100) * predictedPos.sl
                triggersSl = "low"
                triggersTp = "high"
                direction = 1

            elif predictedPos.direction == "short":
                posTp = predictedPos.entryPrice - (predictedPos.entryPrice / 100) * predictedPos.tp
                posSl = predictedPos.entryPrice + (predictedPos.entryPrice / 100) * predictedPos.sl
                triggersSl = "high"
                triggersTp = "low"
                direction = -1

            else:
                raise Exception("Unknown direction")

            # calculate exit index, exit price and profit
            # for each kline after the position opens
            for j in range(i, len(self.klines)):
                currKlineIndex = i + j

                try:
                    currKline = self.klines[currKlineIndex]
                except IndexError:
                    # end of data
                    break

                # first check sl for worst case
                if currKline[triggersSl] * direction < posSl * direction:
                    predictedPos.exitIndex = currKlineIndex
                    predictedPos.exitPrice = posSl
                    stats["losingPositions"].append(predictedPos)

                    break

                # then check tp
                if currKline[triggersTp] * direction > posTp * direction:
                    predictedPos.exitIndex = currKlineIndex
                    predictedPos.exitPrice = posTp
                    stats["winningPositions"].append(predictedPos)

                    break

            # append the position to the correct lists
            stats["totPositions"].append(predictedPos)

            if predictedPos.direction == "long":
                stats["longPositions"].append(predictedPos)

            if predictedPos.direction == "short":
                stats["shortPositions"].append(predictedPos)

        return stats
