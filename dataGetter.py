"""
This file will contain only functions that get data from their data source and return
the usable JSON format

swiss site link: 	https://www.dukascopy.com/swiss/english/fx-market-tools/historical-data/
binance link:		https://www.binance.com/en/landing/data
"""

import csv
from datetime import datetime, timezone, timedelta


def getForexDataSwissSite(filePath="./klineData/swissSiteData/EURUSD_Candlestick_15_M_BID_01.01.2022-01.01.2023.csv"):
	print(f"Getting data from {filePath}")

	klines = []

	with open(filePath, "r") as csvFile:
		csvReader = csv.reader(csvFile)
		# skip first row
		next(csvReader)
		# time, Open, High, Low, Close, Volume
		for row in csvReader:
			dt = datetime.strptime(row[0], "%d.%m.%Y %H:%M:%S.%f %Z%z")
			timestamp = (dt - datetime(1970, 1, 1, tzinfo=timezone.utc)) // timedelta(seconds=1)

			kline = {
				"timestamp": timestamp,
				"open": float(row[1]),
				"high": float(row[2]),
				"low": float(row[3]),
				"close": float(row[4]),
				"volume": float(row[5])
			}

			klines.append(kline)

	print("Done!\n")

	return klines


def getCryptoDataBinance(filePath="./klineData/binanceData/BTCUSDT-1m-2023.csv"):
	print(f"Getting data from {filePath}")

	klines = []

	with open(filePath, "r") as csvFile:
		csvReader = csv.reader(csvFile)
		# skip first row
		next(csvReader)
		# time, Open, High, Low, Close, Volume
		for row in csvReader:
			kline = {
				"timestamp": int(row[0]),
				"open": float(row[1]),
				"high": float(row[2]),
				"low": float(row[3]),
				"close": float(row[4]),
				"volume": float(row[5])
			}

			klines.append(kline)

	print("Done!\n")

	return klines
