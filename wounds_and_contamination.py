import random
from collections import defaultdict


def roll(stats, mod=0):
    r = sorted(random.randint(1, 10) for _ in range(5 + abs(mod)))
    return (sum(r[s - 1 + (mod if mod > 0 else 0)] for s in stats if s > 0),
            {n: r.count(n) - 1 for n in range(1, 11) if r.count(n) > 1})


def add_healing_rate(healing_rate: dict, name: str, fitness_skill: int, healing_bonus_skill: int):
    newheal, resonance = roll((fitness_skill, healing_bonus_skill))
    healing_rate[name] = (max(
        min(newheal, healing_rate.get(" " + name, 999))
        + resonance.get(10, 0), 0) // (resonance.get(1, 0) + 1))

    return resonance.get(1, -1)


def timeformat(hours):
    if hours > 24:
        days = hours / 24
        if days > 30:
            months = days / 30
            if months > 12:
                return str(round(days / 365, 2)) + "y"
            else:
                return str(round(months, 2)) + "m"
        else:
            return str(round(hours / 24, 2)) + "d"
    else:
        return str(hours) + "h"


def testrun(runs, environmental_contamination, resistance_skill, fitness_skill, healing_bonus_skill, health,
            startingcharacon=0, tolerance=0, duration=720):
    mortality = 0
    deathafter = []
    woundstotal = 0
    contatotal = []
    toltotal = []

    for i in range(runs):
        # healing rule (test):
        # one roll is made (after being wounded and while conditions hold)
        # rerolls on receiving damage can only worsen the result
        # threshholds: 3, 5, 7, 9, 11, 13, 15, 17, 19, 20
        # healing level +1 for every threshhold hit
        # all wounds in parallel get compared to healing level.
        log = ""
        healing_thresh = [3, 5, 7, 9, 11, 13, 15, 17, 19, 20]
        exposure = 0
        wounds = defaultdict(int)
        healing_rate = defaultdict(int)
        healing_progress = defaultdict(int)
        character_contamination = startingcharacon
        hours = 0
        while sum(wounds.values()) < health and hours < duration:
            hours += 1
            # log += f"hour:{hours}\t charcon:{character_contamination} wounds:{dict(wounds)}\n"
            resistance, resonance = roll((resistance_skill, fitness_skill))
            resistance = max(resistance - resonance.get(1, 0) + resonance.get(10, 0), 0)
            # environmental wound:
            wound = environmental_contamination - character_contamination - resistance
            if wound > 0:
                log += f"{wounds['Ingress']} Wounded {wound}!\n"
                character_contamination += 1
                wounds["Ingress"] += wound
                # Also (re)roll the healingrate for this wound, take lower
                add_healing_rate(healing_rate, "Ingress", fitness_skill, healing_bonus_skill)
                log += f"Healing rate: {healing_rate['Ingress']}\n"
            if hours % 24 == 0:
                for k in wounds.keys():
                    healing_progress[k] += sum(1 for x in healing_thresh if x <= healing_rate[k])
                    healing_progress[k] -= max(0, character_contamination - tolerance)
                    log += f"healing [k] with progress of {sum(1 for x in healing_thresh if x <= healing_rate[k])} " \
                           f"and regress of {max(0, character_contamination - tolerance)}\n"
                    log += f"Progress: {healing_progress} Wounds: {wounds}\n"
                    if healing_progress[k] >= wounds[k]:
                        wounds[k] = max(wounds[k] - 1, 0)
                        # print("HEALING", k)
                        healing_progress[k] = 0
                    elif healing_progress[k] < 0:
                        healing_progress[k] = wounds[k]
                        wounds[k] += 1
                exposure += character_contamination - tolerance
                if exposure > 300:
                    exposure = 0
                    tolerance += 1

        if hours < duration:
            mortality += 1
            deathafter.append(hours)
            # print(log)
        woundstotal += sum(wounds.values())
        contatotal.append(character_contamination)
        toltotal.append(tolerance)

        # print("run", i, "ended with", dict(wounds), "wounds after", timeformat(hours), "with",
        #      character_contamination, "con")

    print("{env:<3}&{death} \t&{mortality:<5g}% &{wounds} &{con:3.2g}-{tol:.2g} \\\\".format(
        env=environmental_contamination,
        death="none" if len(deathafter) == 0 else timeformat(sum(deathafter) / len(deathafter)),
        mortality=100 * mortality / runs,
        wounds=woundstotal / runs,
        con=sum(contatotal) / len(contatotal),
        tol=sum(toltotal) / len(toltotal)))
    return False



def woundtest(wound, healinglevel, superhealing=False):
    progress = 0
    i = 0
    while wound > 0:
        i += 1
        progress += healinglevel
        if progress >= wound:
            if superhealing:
                s_heal = progress // wound
                progress = progress % wound
                # print(s_heal, progress, wound)
                wound -= s_heal
            else:
                progress = 0
                wound -= 1
        if i > 1000:
            return 999999999
    return i


print("C & death & mortality & wounds & con\\\\")

for c in range(50):
    testrun(runs=100,  # runs
            environmental_contamination=c,
            resistance_skill=1,
            fitness_skill=2,
            healing_bonus_skill=0,
            health=50,
            startingcharacon=0,
            tolerance=0,
            duration=int(4 * 365 * 24))  # hours
