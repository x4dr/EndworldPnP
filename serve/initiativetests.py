import random


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


def manyrolls(amt,lvl):
    return [d10(lvl) for x in range(amt)]


party = {}
partylevels = {"Lvl1": 1, "Lvl2": 2, "Lvl3": 3, "Lvl4": 4, "Lvl5": 5}
score = {x: 0 for x in partylevels.keys()}
rounds = 10000
for i in range(rounds):
    newround(party, partylevels)
    process(party, score)

score = {x: score[x] / rounds for x in score.keys()}
print("average number of actions per round:", score)

avgdiff = 0
hits = 0

print("average number for the levels:", sum(manyrolls(1000,1))/1000,
      sum(manyrolls(1000, 2)) / 1000,
      sum(manyrolls(1000, 3)) / 1000,
      sum(manyrolls(1000, 4)) / 1000,
      sum(manyrolls(1000, 5)) / 1000,)
for i in range(rounds):
    a = d10(3)
    b = d10(3) - 1
    hits += 1 if b >= a else 0
    avgdiff += b - a if a <= b else 0
print(avgdiff / hits, hits / rounds)
