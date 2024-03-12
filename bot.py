"""
The main body of the bot, where everything will be run from
"""

import matplotlib.pyplot as plt
from matplotlib.collections import PatchCollection
from matplotlib.patches import Rectangle

from decisionMaker import Knn
from dataGetter import getForexDataSwissSite


def backtest(data, decisionMaker):
    """
    Runs a backtest on given data using given decisionMaker

    :return:
    """
    pass


def plotChart(chart):
    """
    Plots given chart

    :return:
    """

    pass


def plotKlines(klines, hlWidth=0.1, lineHeight=0.001, bullishColor="green", bearishColor="red", rangingColor="yellow"):
    print("Plotting...")

    fig = plt.figure()
    gs = fig.add_gridspec(2, 1, hspace=0, height_ratios=[3, 1])
    axs = gs.subplots(sharex=True)
    bullish = []
    bearish = []
    ranging = []

    for index in range(len(klines)):
        kline = klines[index]

        coords = (index, kline["open"])  # (index, openPrice)
        width = 1  # 1, because each index is large 1
        height = kline["close"] - kline["open"]  # closePrice - openPrice

        coordsHl = (((index + 0.5) - hlWidth / 2), kline["low"])
        heightHl = kline["high"] - kline["low"]

        if height > 0:
            bullish.append(Rectangle(coords, width, height))
            bullish.append(Rectangle(coordsHl, hlWidth, heightHl))
        elif height < 0:
            bearish.append(Rectangle(coords, width, height))
            bearish.append(Rectangle(coordsHl, hlWidth, heightHl))
        else:
            ranging.append(Rectangle(coords, width, lineHeight))

    axs[0].add_collection(PatchCollection(bullish, edgecolor="none", facecolor=bullishColor))
    axs[0].add_collection(PatchCollection(bearish, edgecolor="none", facecolor=bearishColor))
    axs[0].add_collection(PatchCollection(ranging, edgecolor="none", facecolor=rangingColor))

    axs[0].errorbar(0, 0)

    # plot volume
    axs[1].plot(range(len(klines)), [kline["volume"] for kline in klines])

    for ax in axs:
        ax.label_outer()

    plt.tight_layout()

    axs[0].grid(True)
    axs[1].grid(True)
    plt.show()

    print("Done!\n")


if __name__ == '__main__':
    # get klines
    klines = getForexDataSwissSite()

    # split it into training and simulation data
    trainKlines = klines[:30000]
    simKlines = klines[30000:]

    plotKlines(simKlines)
