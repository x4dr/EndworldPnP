import random


def roll(stats, mod=0):
    r = sorted(random.randint(1, 10) for _ in range(5 + abs(mod)))
    return sum(r[s - 1 + mod if mod > 0 else 0] for s in stats if s > 0)


def deflect(mod):
    return sorted(
        [random.randint(1, 10) for _ in range(abs(mod) + 1)], reverse=mod > 0
    )[0]


class ArmorStack(object):
    def __init__(self, depth, stats):
        self.layers = []
        stat = (0, 0)
        for i in range(depth):
            if i < len(stats):
                stat = tuple(stats[i])
            self.layers.append(stat)

    def damage(self, damage):
        if damage <= 0:
            return True
        if len(self.layers) == 0:
            return False
        damage = damage - roll(self.layers[-1])
        if damage >= 0:
            self.layers.pop()
            print("armor lost!", self.layers, damage)
            return self.damage(damage)
        else:
            return True

    @property
    def sturdyness(self):
        return sum(sum(x) for x in self.layers)


class Weapon(object):
    def __init__(self, atk, cd, threshholds=None):
        if threshholds is None:
            self.threshholds = [5, 8, 11, 14, 17]
        self.attack = atk
        self.cooldown = cd
        self.state = 0


class Pilot(object):
    def __init__(self, attackstats, defensestats):
        self.attackStats = attackstats
        self.defendStats = defensestats


class Mech(object):
    def __init__(self, width, depths, statss, wpn=None, plt=None, defthresh=None):
        if defthresh is None:
            defthresh = [5, 8, 11, 14, 17]
        if plt is None:
            plt = Pilot((1, 0), (1, 0))
        if wpn is None:
            wpn = Weapon(10, 1)
        self.defenseThreshhold = defthresh
        self.armorStacks = []
        depth = 0
        stats = []
        for i in range(width):
            if i < len(depths):
                depth = depths[i]
            if i < len(statss):
                stats = statss[i]
            self.armorStacks.append(ArmorStack(depth, stats))
        self.weapon = wpn
        self.pilot = plt

    def __repr__(self):
        return "-".join(["#" * len(x.layers) for x in self.armorStacks])

    def damage(self, damage, adv, target):
        if not adv > 0:
            print("not even a good shot!")
            return False
        defenseroll = roll(self.pilot.attackStats)
        defense = sum(1 if t <= defenseroll else 0 for t in self.defenseThreshhold)
        deviance = 10 - deflect(adv - defense)
        locations = [target + deviance, target - deviance]
        locations = [
            loc if 0 <= loc < len(self.armorStacks) else None for loc in locations
        ]
        print(
            f"defending with {defense} from  roll {defenseroll} and a deviance of {deviance}, possible targets are {locations}"
        )
        if None in locations:  # possibility to miss
            print("so a miss it is")
            return False  # miss
        location = max(
            locations, key=lambda x: self.armorStacks[x].sturdyness
        )  # defender selects sturdier armor
        return not self.armorStacks[location].damage(damage)

    def attack(self, target: "Mech"):
        if self.weapon.state > 0:
            self.weapon.state -= 1
            print("cd...")
            return False
        self.weapon.state = self.weapon.cooldown
        levels = roll(self.pilot.attackStats)
        advantage = sum(1 if t <= levels else 0 for t in self.weapon.threshholds)
        print(
            f"attacking with {advantage} advantage from rolled {levels} and "
            f"{self.weapon.attack} damage at {len(target.armorStacks) // 2 + 1}"
        )
        return target.damage(
            self.weapon.attack, advantage, len(target.armorStacks) // 2 + 1
        )


if __name__ == "__main__":
    mech1 = Mech(8, [3], [((2, 3),)], Weapon(10, 1), Pilot((2, 3), (2, 3)))
    mech2 = Mech(5, [4], [((2, 3),)], Weapon(10, 1), Pilot((2, 3), (2, 3)))

    for combatRound in range(2000):
        print(combatRound)
        print(mech1)
        print(mech2)
        if mech1.attack(mech2):
            print("MECH1 WINS")
            break
        if mech2.attack(mech1):
            print("MECH2 WINS")
            break
