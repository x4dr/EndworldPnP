import random

import numpy

from serve import maxspeed


def d10(lvl):
    amt = abs(lvl - 3) + 1
    desc = lvl - 3 < 0
    x = sorted([random.randint(1, 10) for i in range(amt)], reverse=desc)
    for i in range(len(x)):
        if x[i:].count(x[i]) > 1:
            x.append((x.count(x[i]) - 1) * (-1 if desc else 1) + x[i])

    return min(x) if desc else max(x)


def initiative(lvl, bonus):
    ini = bonus
    ini += d10(lvl)
    return ini


def process(actors, acted, actioncost=6):
    while any(x > actioncost for x in actors.values()):
        for actor in actors.keys():
            if all(actors[actor] >= x for x in actors.values()):
                acted[actor] += 1
                #           print(actor, actors[actor])
                actors[actor] -= actioncost
                break


def newround(actors, actorlevels):
    for a in actorlevels.keys():
        actors[a] = actors.get(a, 0) + initiative(actorlevels[a], 3)
        # print("new round", actors)


def manyrolls(amt, lvl):
    return [d10(lvl) for x in range(amt)]


res = []
for m in range(10):
    res.append([])
    for p in range(500):
        res[-1].append(maxspeed((m + 2) * 5000, (p * 10000), 5, 0.12, 0))


if __name__ == "__main__":
    import matplotlib.pyplot as plt

    i = 0
    for x in res:
        plt.plot(x, label=f"{(i+2)*5} t")
        i += 1
        plt.legend()
    plt.plot(list(10*numpy.log(x) for x in range(500)))
    plt.show()
