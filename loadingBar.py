def loadingBar(currentNum, totalNum, msgBefore="", msgAfter="", length=30, fill='█', prefix=''):
    ratio = totalNum // length
    barProg = int(currentNum / ratio)
    bar = fill * barProg + '-' * int(length - barProg)
    print(f'\r{msgBefore}{prefix} |{bar}| {round(((currentNum / totalNum) * 100), 1)}% Complete {msgAfter}', end="", flush=True)
