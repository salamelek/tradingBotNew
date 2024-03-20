# the configuration for the simulated positions
positionSimConfig = {
    "sl": 0.3,     # in PERCENTS
    "tp": 0.3,
    "maxLength": 15,
    "minLength": 1,
    "max chop": 1
}


# the parameters for the knn algo
knnConfig = {
    "k": 6,
    # "threshold": 0.000001,    # forex
    "threshold": 0.05,
    "sameDirectionRatio": 0.9
}
