"""
The main body of the bot, where everything will be run from
"""

import matplotlib.pyplot as plt

from decisionMaker import Knn
from dataGetter import getForexDataSwissSite, getCryptoDataBinance
from tradingClasses import Chart


def backtest(data, decisionMaker):
    """
    Runs a backtest on given data using given decisionMaker

    Returns a dictionary with all the results of the backtest

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
    # klines = getForexDataSwissSite()
    klines = getCryptoDataBinance()

    # THIS HAS OVER 500000 KLINES, DO *NOT* ATTEMPT TO PLOT
    chart = Chart(klines)
    # THIS HAS OVER 500000 KLINES, DO *NOT* ATTEMPT TO PLOT

    # split it into training and simulation data
    trainKlines = klines[:500000]
    simKlines = klines[500000:]

    brain = Knn(trainKlines)

    predictedPositions = []
    for i in range(30, 70):
        positions = brain.getPosition(simKlines, i)
        predictedPositions.append(positions["predicted"])
        if i % 10 == 0:
            print(f"{i}/1000")

    chart = Chart(simKlines, positions=predictedPositions)
    plotChart(chart)
    # print(chart)
