# the configuration for the simulated positions
positionSimConfig = {
    "sl": 0.1,     # in PERCENTS
    "tp": 0.2,
    "maxLength": 10,
    "minLength": 1,
    "max chop": 1
}


# the parameters for the knn algo
knnConfig = {
    "k": 6,
    # "threshold": 0.000001,    # forex
    "threshold": 0.05,
    "sameDirectionRatio": 1
}


# check that every parameter makes sense
if knnConfig["sameDirectionRatio"] < 0.5:
    # only the highest ratio gets compared, so it will always be >= 0.5
    raise Exception("The same direction ratio must be >= 0.5!")

if knnConfig["threshold"] <= 0:
    raise Exception("The threshold must be greater than 0!")

# TODO add boundaries for tp, sl and everything else too
