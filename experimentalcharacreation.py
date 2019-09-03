import time


def costcalc(level, start=1):
    return sum([x * x for x in range(start + 1, level + 1)])


def skillcalc(skills, start=1):
    return sum(costcalc(i, start) for i in skills)


def distcalc(distribution, start=1):
    return sum([costcalc(di, start) * distribution[di - 1] for di in range(1, len(distribution) + 1)])


def couldraise(remainingpoints, skills, start=0):
    remainingpoints -= skillcalc(skills, start)
    for s in skills:
        if costcalc(s + 1, start) <= remainingpoints:
            # print("in", skills, s, "could have been raised for", costcalc(s+1,start), "leftover:",remainingpoints)
            return True

    return False


def searchdist(length, amt, dist=None):
    if dist is None:
        dist = []
    if sum(dist) > amt:
        return []
    if len(dist) < length:
        valid = []
        for d in range(amt + 1 - sum(dist)):
            for v in searchdist(length, amt, dist + [d]):
                valid.append(v)
        return valid
    else:
        if sum(dist) != amt:
            return []
        else:
            return [dist]


def searchall(points, skills, start=1, differentskills=9):
    if skillcalc(skills, start) > points:
        return []
    if len(skills) < differentskills:
        valid = []
        for level in [1, 2, 3, 4, 5]:
            for r in searchall(points, skills + [level], start):
                valid.append(r)
        return valid
    else:
        if not couldraise(points, skills, start):
            # print(skills, sum(skills))
            return [skills]
        else:
            return []


print("selftest: \nattr lvl 1: {lvl1}\n"
      "attr lvl 2: {lvl2}\n"
      "attr lvl 3: {lvl3}\n"
      "attr lvl 4: {lvl4}\n"
      "attr lvl 5: {lvl5}\n"
      .format(lvl1=costcalc(1, 1),
              lvl2=costcalc(2, 1),
              lvl3=costcalc(3, 1),
              lvl4=costcalc(4, 1),
              lvl5=costcalc(5, 1)))

time1 = time.time()
dists = searchdist(10, 20)
print("time:", time.time() - time1)
print(len(dists))

found = searchall(0, [], 1)
if found:
    print(len(found))

    distri = []
    for f in found:
        used = [0] * 5
        for i in range(1, 6):
            used[i - 1] = f.count(i)
        distri.append(used)
    distri = {str(x): distri.count(x) for x in distri}

    for dk in distri.keys():
        print(dk, "\t\t", distri[dk])
