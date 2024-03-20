import pandas as pd
import os


folderPath = "ETHUSDT-1m-2023"
allFiles = os.listdir(folderPath)
csvFiles = [f for f in allFiles if f.endswith('.csv')]

# Sort the list of CSV files
csvFiles = sorted(csvFiles)

# Create a list to hold the dataframes
dfList = []

for csv in csvFiles:
    filePath = os.path.join(folderPath, csv)

    try:
        # Try reading the file using default UTF-8 encoding
        df = pd.read_csv(filePath, usecols=[0, 1, 2, 3, 4, 5], header=None, names=["timestamp", "open", "high", "low", "close", "volume"])

        if df["open"][0] == "open":
            df = df.drop(df.index[0])
            df = df.reset_index(drop=True)

        df["timestamp"] = df["timestamp"].astype(int)
        df["open"] = df["open"].astype(float)
        df["high"] = df["high"].astype(float)
        df["low"] = df["low"].astype(float)
        df["close"] = df["close"].astype(float)
        df["volume"] = df["volume"].astype(float)

        dfList.append(df)

    except Exception as e:
        print(f"Could not read file {csv} because of error: {e}")

# Concatenate all data into one DataFrame
big_df = pd.concat(dfList, ignore_index=True)

# Save the final result to a new CSV file
big_df.to_csv(os.path.join("./", f"{folderPath}.csv"), index=False)
