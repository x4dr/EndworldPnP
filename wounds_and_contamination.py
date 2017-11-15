import random


def d10(lvl):
    amt = abs(lvl - 3) + 1
    desc = lvl - 3 < 0
    x = sorted([random.randint(1, 10) for i in range(amt)], reverse=desc)
    for i in range(len(x)):
        if x[i:].count(x[i]) > 1:
            x.append((x.count(x[i]) - 1) * (-1 if desc else 1) + x[i])

    return min(x) if desc else max(x)


def testrun(runs, env, res, fit, health, resmod, extres=0, startingcharataint=0, duration=720):
    mortality = 0
    tod = []
    avgwoundstotal = 0
    contatotal = []
    brk = 0
    for i in range(runs):

        wounds = []
        conta = startingcharataint
        hours = 0
        avgwounds = 0
        while len(wounds) < health and hours < duration:
            hours += 1
            avgwounds += len(wounds)
            if avgwounds == 0 and hours > 25:  # if nothing occured in the first day
                hours = duration  # probably nothing will
                continue  # skips instances where damage was healed the hour it was suffered... but yeah
            if not (hours < 48 or hours % 24 == 0):
                continue

            # print("hour:", hours, "\t charcon:", conta, "wounds:", wounds)
            wound = d10(res)
            # if env - conta > res - 2:
            # print("receiving", (env - conta - resmod), "environmental damage, reducing by", wound)
            wound = (env - conta - resmod - extres) - wound
            if wound > 0:
                if fit:
                    conta += 1
                # print("hurt from", env, "with difficulty", wound)
                if wound > 10:
                    wounds.append(10)
                    wound -= 10
                wounds.append(wound)
            if hours % 24 == 0 and fit:
                healing = True
                heal = d10(res)
                wound = conta - resmod - heal
                #    print("resisting internal contamination of", conta, " with mod", resmod, "with roll", heal)
                if wound > 0:
                    #        print("wasting away from being Contaminated:", wound)
                    wounds.append(wound)
                    healing = False

                for w in range(len(wounds)):
                    difficulty = abs(wounds[w]) + len(wounds) - 1
                    heal = d10(fit)
                    # if healing:
                    #    print("trying to heal", difficulty, "with", heal, "!")
                    # else:
                    #    print("trying not to be 5 under", difficulty, "with", heal, "!")
                    reco = heal - difficulty
                    if reco > 0 and healing:
                        if wounds[w] > 0:
                            wounds[w] -= 1
                        else:
                            wounds[w] = abs(wounds[w])
                            # print("success!")
                    elif reco <= -5:
                        if wounds[w] < 0:
                            # print("infection!")
                            wounds.append(int(abs(wounds[w]) / 2))
                        else:
                            wounds[w] *= -1
                wounds = [w if w > 0 else w - 1 for w in wounds if w != 0]
        if hours < duration:
            mortality += 1
            tod.append(hours)
        avgwoundstotal += avgwounds / hours
        contatotal.append(conta)
        # print("run", i, "ended with", wounds, "wounds after", hours, "hours, having", avgwounds / hours,
        #      " wounds on average")
    # if abs((avgwoundstotal - (((health / 2) - 1) * (i + 1)))) < 0.0001:
    #    return True
    if avgwoundstotal or 1:
        print(("{0:<3}&{1:{form}} \t&{2:<5g}% &{3:>6.2g} " + ("&{4:>6.2g} " if fit else "") + "\\\\").format(
            env,
            "none" if len(tod) == 0 else (sum(tod) / len(tod)),
            100 * mortality / (i + 1),
            int(avgwoundstotal / (i + 1)),
            sum(contatotal) / len(contatotal), form=6 if len(tod) == 0 else "6.2f"))
    return False


CatA = {"Cat": "A", "HP": 8, "Resistance Category": 3, "Fitness": 3, "Internal Resistance": -1,
        "Starting Contamination": 0, "External Resistance": 0}
CatB = {"Cat": "B", "HP": 10, "Resistance Category": 4, "Fitness": 3, "Internal Resistance": 0,
        "Starting Contamination": 2, "External Resistance": 0}
CatC = {"Cat": "C", "HP": 12, "Resistance Category": 5, "Fitness": 3, "Internal Resistance": 1,
        "Starting Contamination": 3, "External Resistance": 0}

ET = {"Cat": "ET", "HP": 10, "Resistance Category": 1, "Fitness": 0, "Internal Resistance": -1,
      "Starting Contamination": 0, "External Resistance": 0}
HT = {"Cat": "HT", "HP": 10, "Resistance Category": 2, "Fitness": 0, "Internal Resistance": 0,
      "Starting Contamination": 0, "External Resistance": 0}
MT = {"Cat": "MT", "HP": 10, "Resistance Category": 3, "Fitness": 0, "Internal Resistance": 1,
      "Starting Contamination": 0, "External Resistance": 0}
LT = {"Cat": "LT", "HP": 10, "Resistance Category": 4, "Fitness": 0, "Internal Resistance": 2,
      "Starting Contamination": 0, "External Resistance": 0}
BT = {"Cat": "BT", "HP": 10, "Resistance Category": 5, "Fitness": 0, "Internal Resistance": 3,
      "Starting Contamination": 0, "External Resistance": 0}

for chara in [
    # CatA, CatB, CatC
    ET,
    HT,
    MT, LT, BT
]:
    if chara["Fitness"] == 0:
        print("TechLevel:", chara["Cat"], " \\\\\nC & failure & failurerate & damage\\\\")
    else:
        print("Category:", chara["Cat"], " \\\\\nC & death & mortality & wounds & con\\\\")
    for env in [0,2, 8]:#range(0, 8, 3):
        if testrun(1000, env,
                   chara["Resistance Category"],
                   chara["Fitness"],
                   chara["HP"],
                   chara["Internal Resistance"],
                   chara["External Resistance"],
                   chara["Starting Contamination"],
                   720):
            break
