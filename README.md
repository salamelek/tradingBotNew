# Trading bot / AI

## Modules

### DataGetter

All the data that will be stored is: timestamp, open, high, low, close, volume data. 

Timestamp data will be used for training: 
you can't just strip out weekends of inactive charts, you have to consider them in training

All the indicators should be calculated by the bot itself, so the stored data is only the required one.

---

#### Data format

But how will this data be stored? I usually use csv files, but other options are databases and http requests.
The problem is not actually storing it, but rather using it from any source. I guess I'll just use some kind of 
json format and then make an arbitrary set of connectors for any input of data

```
kline data csv -------> connector1 ═╗ 
kline data http ------> connector2 ═╬══> trading bot
kline data database --> connector3 ═╝ 
```

The only task of a connector will be to read the data in the given format and reformat it into the format used by 
the trading bot. This should be a small enough task.

Now, there are two options that I'm considering regarding the usable format: 
pandas or json? I think I'll go with a json format since that's what I'm used to and its 100% customisable. 
Pandas might be handy for whole dataframe operations, but it's nothing a function cant handle.

But how to actually store the data in a json format? 

1) list of klines `[{"timestamp": 2398..., "open": 123, ...}, {...}, {...}, ...]`
2) dict of klines based on timestamp: `{100000: {"open": 123, "close": 132, ...}, 100001: {...}, ...}`
3) dict of values lists: `{"timestamp": [123, 123, ...], "open": [1, 2, ...], ...}`

I think that approach 2 is completely useless, so I won't consider it. Both the 1st and 3rd approach are valid,
but looping through all the candles is better I think, so I'll use the approach 1.

### Bot

I want the bot to be completely modular: if you want to change the data source, just change the connector.
If you want to change the indicators, change that module only. Want to change the decision logic? Go there and change
JUST THAT. This means that it should also be able to switch between let's say KNN and qLearning approaches.

List of features:
- [x] Dynamic data source (choose freely where to get data from)
- [ ] Dynamic decision logic (choose what model to use)
- [ ] Backtest visually
- [ ] Place testnet orders via API

### DecisionMaker

## Plotting

To plot everything, I will use classes, to make everything organised.

### Chart
This class will hold the klines, dataPoints/indicators and positions.

### Indicators
This class will calculate the indicator

### Position
This class will hold the index, entry price, direction, sl, tp, exit price and profit of the position