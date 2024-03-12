"""
The main body of the bot, where everything will be run from
"""

import matplotlib.pyplot as plt
from matplotlib.collections import PatchCollection
from matplotlib.patches import Rectangle

from decisionMaker import Knn
from dataGetter import getForexDataSwissSite
from PlotClasses import Chart


def backtest(data, decisionMaker):
    """
    Runs a backtest on given data using given decisionMaker

    :return:
    """
    pass


def plotChart(chart, extraSeries=(), dataPoints=((),)):
    """
    Plots given chart and all of its components
    """

    print("Plotting...")

    fig = plt.figure()
    gs = fig.add_gridspec(2, 1, hspace=0, height_ratios=[4, 1])
    axs = gs.subplots(sharex=True)

    # plot chart (with indicators and positions)
    chart.plot(axs)

    # plot additional series
    for series in extraSeries:
        axs[0].plot(range(len(series)), series)

    # plot given dataPoints
    for dimIndex in range(len(dataPoints[0])):
        axs[0].plot(range(len(dataPoints)), [dp[dimIndex] for dp in dataPoints], label=dimIndex)

    for ax in axs:
        ax.label_outer()

    plt.tight_layout()

    axs[0].grid(True)
    axs[1].grid(True)
    # axs[0].legend()
    plt.show()

    print("Done!\n")


if __name__ == '__main__':
    # get klines
    klines = getForexDataSwissSite()

    # split it into training and simulation data
    trainKlines = klines[:30000]
    simKlines = klines[30000:]

    brain = Knn(trainKlines)

    chart = Chart(klines)
    # plotChart(chart)
    print(chart)
