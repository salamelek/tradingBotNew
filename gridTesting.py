"""
Just a test file to test grid separation of knn datapoints
"""

import numpy as np
import matplotlib.pyplot as plt
from dataGetter import getCryptoDataBinance
import time
from config import knnConfig


def euclideanDistance(a, b):
    dist = 0

    for i in range(len(a)):
        dist += (a[i] - b[i]) ** 2

    return np.sqrt(dist)


def extractDataPoints(klines):
    dataPoints = []

    for i in range(len(klines)):
        kline = klines[i]

        dp = [
            kline["close"] - kline["open"],  # price change
            kline["volume"],  # volume
        ]

        dataPoints.append(dp)

    return dataPoints


def plotPoints():
    print("Plotting points...")

    x = [point[0] for point in dataPoints]
    y = [point[1] for point in dataPoints]

    # Plotting the points
    plt.scatter(x, y)

    # Adding labels and title
    plt.xlabel('price change')
    plt.ylabel('volume')
    plt.title('Scatter Plot of Points')

    # Displaying the plot
    plt.show()


def distributeDp(dataPoints):
    print("distributing...")

    aQuadEvery = 10
    distributedDp = {}

    for dp in dataPoints:
        key = (dp[0] // knnConfig["threshold"], dp[1] // knnConfig["threshold"])

        try:
            distributedDp[key].append(dp)
        except KeyError:
            distributedDp[key] = [dp]

    print("Done!")

    return distributedDp


def getEverySquareRecursive(centerSquare):
    pass


def getKnnNew(distributedDp, dataPoint, k=3):
    """
    about 200x faster than old

    :param distributedDp:
    :param dataPoint:
    :param k:
    :return:
    """

    key = []
    for i in range(len(dataPoint)):
        key.append(int(dataPoint[i] // knnConfig["threshold"]))

    closeNn = []

    for k1 in range(key[0] - 1, key[0] + 2):
        for k2 in range(key[1] - 1, key[1] + 2):
            try:
                closeNn += distributedDp[(k1, k2)]
            except KeyError:
                pass

    if len(closeNn) < k:
        return None

    knn = []

    for index in range(len(closeNn)):
        trainDp = closeNn[index]

        distance = euclideanDistance(trainDp, dataPoint)

        neighbour = {"distance": distance, "index": index}

        # if the list is still empty, just append the neighbour
        if len(knn) < k:
            knn.append(neighbour)
            continue

        # sort the neighbours (for easier access)
        # lower distance first, higher at the end
        knn = sorted(knn, key=lambda x: x["distance"])

        # replace the worst neighbour with the better one
        if distance < knn[-1]["distance"]:
            knn[-1] = neighbour

    return knn


def getKnnOld(dataPoint, dataPoints, k=3):
    """
    about 15 seconds for 10 klines
    :param dataPoint:
    :param dataPoints:
    :param k:
    :return:
    """

    knn = []

    for index in range(len(dataPoints)):
        trainDp = dataPoints[index]

        distance = euclideanDistance(trainDp, dataPoint)

        neighbour = {"distance": distance, "index": index}

        # if the list is still empty, just append the neighbour
        if len(knn) < k:
            knn.append(neighbour)
            continue

        # sort the neighbours (for easier access)
        # lower distance first, higher at the end
        knn = sorted(knn, key=lambda x: x["distance"])

        # replace the worst neighbour with the better one
        if distance < knn[-1]["distance"]:
            knn[-1] = neighbour

    return knn


if __name__ == '__main__':
    klines = getCryptoDataBinance()
    dataPoints = extractDataPoints(klines)
    distributedDp = distributeDp(dataPoints)

    # plotPoints()

    start = time.time()

    for i in range(200):
        # loadingBar(i, 100)
        dp = dataPoints[i]
        new = getKnnNew(distributedDp, dp)
        old = getKnnOld(dp, dataPoints)
        print(f"New: {new[0]['distance']}, {new[2]['distance']}, {new[2]['distance']}")
        print(f"Old: {old[0]['distance']}, {old[2]['distance']}, {old[2]['distance']}")
        print()

    print(f"New ended in {time.time() - start} seconds!")
