import random
import sys

import time
from typing import DefaultDict


def d10(amt, diff, ones=True):  # faster than the WoDDice
    succ = 0
    anti = 0
    for i in range(amt):
        x = random.randint(1, 10)
        if x >= diff:
            succ += 1
        if ones and x == 1:
            anti += 1
    if anti > 0:
        if succ > anti:
            return succ - anti
        else:
            if succ > 0:
                return 0
            else:
                return 0 - anti
    else:
        return succ


def d10h(amt, diff=0):
    x = [random.randint(1, 10) for i in range(abs(amt))]
    if amt > 0:
        for i in range(1, 12):
            if x.count(i) > 1:
                x.append(i + (x.count(i) - 1))
        return max(x) - diff
    elif amt < 0:
        for i in reversed(range(11)):
            if x.count(i) > 1:
                x.append(i - (x.count(i) - 1))
        return min(x) - diff
    else:
        return max(x)


def plot(data):
    success = sum([v for k, v in data.items() if k > 0])
    zeros = sum([v for k, v in data.items() if k == 0])
    botches = sum([v for k, v in data.items() if k < 0])
    total = sum([v for k, v in data.items()])
    pt = total / 100
    print("Of the %d rolls, %d where successes, %d where failures and %d where botches, averaging %.2f" % (
        total, success, zeros, botches, (sum([k * v for k, v in data.items()]) / total)))
    print("The percentages are:\n+ : %.3f%%\n0 : %.3f%%\n- : %.3f%%" % (success / pt, zeros / pt, botches / pt))
    width = 1
    barsuc = int((success / pt) / width)
    barbot = int((botches / pt) / width)
    barzer = int(100 / width - barsuc - barbot)
    print("+" * barsuc + "0" * barzer + "-" * barbot)
    lowest = min(data.keys())
    highest = max(data.keys())
    for i in range(lowest, highest + 1):
        if i == 0:
            print()
        print("%2d : %7.3f%% " % (i, data.get(i, 0) / pt), end="")
        print("#" * int((data.get(i, 0) / pt) / width))
        if i == 0:
            print()


def run():
    roller = d10

    if len(sys.argv) > 3:
        roller = d10h
        duration = float(sys.argv[1])
        amount = int(sys.argv[2])
        difficulty = int(sys.argv[3])
    else:
        print("usage: <duration> <dice amount> <bonus> [d/c/h] [if c compare roll] [nofail]")
        exit()
    if sys.argv[4] == "d":
        roller = d10
    else:
        roller=d10h
    successes = DefaultDict(lambda: 0)
    i = 0
    time1 = time.time()
    compare = len(sys.argv) > 4 and sys.argv[4] == "c"
    bonus = difficulty if compare else 0
    while True:
        i += 1
        if compare:
            difficulty = roller(int(sys.argv[5]))+bonus
        successes[roller(amount, difficulty)] += 1
        if i % 10000 == 0:
            if time.time() - time1 >= duration:
                break
    if "nofail" in sys.argv:
        for key in range(min(successes.keys()),0):
            del(successes[key])
    

    print("rolling %+d %s against %+d %sfor %.1f seconds" % (
    amount,
    "dice" if not compare else "advantage",
    difficulty if not compare else int(sys.argv[5]),
    "" if not compare else "advantage ",
    duration))
    plot(dict(successes))


run()
