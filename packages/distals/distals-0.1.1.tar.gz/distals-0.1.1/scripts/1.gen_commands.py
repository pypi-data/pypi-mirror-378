for i in range(64):
    start = 125 * i
    end = start + 125
    cmd = 'python3 scripts/1.calculate.py ' + str(start) + ' ' + str(end)
    print(cmd)
