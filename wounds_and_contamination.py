import random
from collections import defaultdict

from dask.distributed import Client
import numpy as np
from numba import njit

client = Client(address="tcp://127.0.0.1:8786")


@njit
def roll(stats):
    r = np.sort(np.random.randint(1, 11, 5))
    f = []
    for i in np.arange(1, 11):
        f.append((r == i).sum())
    stats = stats[stats != 0] - 1
    s = np.sum(np.take(r, stats))
    return s, f


def add_healing_rate(healing_rate: dict, name: str, fitness_skill: int, healing_bonus_skill: int):
    newheal, resonance = roll(np.array((fitness_skill, healing_bonus_skill)))
    healing_rate[name] = (max(
        min(newheal, healing_rate.get(" " + name, 999))
        + resonance[9], 0) // (resonance[0] + 1))

    return resonance[0]


def timeformat(hours):
    years = hours // 8760
    hours -= years * 8760
    months = hours // 720
    hours -= months * 720
    days = hours // 24
    hours -= days * 24
    return " ".join([x for x in [
        f"{years:g}y" if years else "",
        f"{months:g}m" if months else "",
        f"{days:g}d" if days else "",
        f"{hours:.2f}h" if hours else ""
    ] if x])


def singletest(inp):
    environmental_contamination = inp['environmental_contamination']
    resistance_skill = inp['resistance_skill']
    fitness_skill = inp['fitness_skill']
    healing_bonus_skill = inp['healing_bonus_skill']
    health = inp['health']
    startingcharacon = inp['startingcharacon']
    tolerance = inp['tolerance']
    duration = inp['duration']
    log = ""
    healing_thresh = [3, 5, 7, 9, 11, 13, 15, 17, 19, 20]
    wounds = defaultdict(int)
    healing_rate = defaultdict(int)
    healing_progress = defaultdict(int)
    character_contamination = startingcharacon
    hours = 0
    while sum(wounds.values()) < health and hours < duration:
        hours += 1
        # log += f"hour:{hours}\t charcon:{character_contamination} wounds:{dict(wounds)}\n"
        resistance, resonance = roll(np.array((resistance_skill, fitness_skill)))
        resistance = resistance - resonance[0] + resonance[9]
        resistance = resistance if resistance > 0 else 0
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
    if hours < duration:
        mortality = 1
        deathafter = hours
        # print(log)
    else:
        mortality = 0
        deathafter = 0

    woundstotal = sum(wounds.values())
    contatotal = character_contamination
    return environmental_contamination, mortality, deathafter, woundstotal, contatotal

    # print("run", i, "ended with", dict(wounds), "wounds after", timeformat(hours), "with",
    #      character_contamination, "con")


def glomp(x):
    mortality = 0
    deathafter = []
    woundstotal = 0
    contatotal = []
    env = 0
    for i in x:
        env, mortalityres, deathafterres, woundstotalres, contatotalres = i
        mortality += mortalityres
        deathafter.append(deathafterres)
        woundstotal += woundstotalres
        contatotal.append(contatotalres)
    return dict(
        env=env,
        death="none" if len(deathafter) == 0 else timeformat(sum(deathafter) / len(deathafter)),
        mortality=100 * mortality / len(x),
        wounds=woundstotal / len(x),
        con=sum(contatotal) / len(contatotal))


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
        if i > 10000:
            return 999999999
    return i


for severity in range(91, 26):
    print(f"{severity} & ", end="")
    for regen in range(1, 11):
        print(f" {woundtest(severity, regen)} d ", end="&" if regen < 10 else "\n")

print("resistances & con & deathtime & mortality & avg wounds & conta\\\\")
for rs in range(5):
    rundata = [
        [client.submit(singletest,
                       dict(run=repeat, environmental_contamination=con, resistance_skill=rs, fitness_skill=2,
                            healing_bonus_skill=0, health=50, startingcharacon=0, tolerance=0,
                            duration=365 * 24))
         for repeat in range(10)]
        for con in range(1, 26)]

    rundata = [client.submit(glomp, r) for r in rundata]

    try:
        for d in rundata:
            d = d.result()
            print(f"{rs + 1} & {d['env']:<3}&{d['death']} \t&{d['mortality']:<3g}% \\\\")
    except Exception as e:
        for x in e.args:
            print(x)
