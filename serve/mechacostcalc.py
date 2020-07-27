from serve import mechdata
from serve.mechdata import sizes
from matplotlib import pyplot as plt

MODULECOSTS = [4, 5, 6, 7, 8]
TECHLEVELS = ["B", "L", "M", "H", "E"]


class Mech:
    def __init__(self, modules):
        self.modules = modules

    @property
    def techlevel(self):
        return TECHLEVELS[max(m.techlevel for m in self.modules)]

    @property  # 2 m -s = s*s
    def sizeclass(self):
        s = 0
        m = 2 * self.moduleamt
        while m - s - 1 > s * s:
            s += +1
        return round(s, 2)

    @property
    def moduleamt(self):
        return sum(m.size for m in self.modules)

    @property
    def weight(self):
        return sum(
            (
                m.weight
                - m.weight
                * 0.08
                * (m.special.get("MaxCargo", 0) - m.special.get("CurrentCargo", 0))
            )
            * m.special.get("WeightMultiplier", 1)
            for m in self.modules
        )

    @property
    def propulsion(self):
        return sum(m.special.get("Propulsion", 0) for m in self.modules)

    @property
    def speedpercent(self):
        return round(100 * self.propulsion / self.weight, 5)

    @property
    def modulecosts(self):
        return sum(MODULECOSTS[m.techlevel] * m.size for m in self.modules)

    @property
    def power_idle(self):
        return round(sum(m.poweridle for m in self.modules), 5)

    @property
    def power_active(self):
        return round(sum(m.poweractive for m in self.modules), 5)

    @property
    def heat_active(self):
        return round(sum(m.heatactive for m in self.modules), 5)

    @property
    def heat_idle(self):
        return round(sum(m.heatidle for m in self.modules), 5)

    @property
    def energy_storage(self):
        return round(sum(m.special.get("EnergyStorage", 0) for m in self.modules), 5)

    @property
    def heat_storage(self):
        return round(sum(m.special.get("HeatStorage", 0) for m in self.modules), 5)

    @property
    def energy_time(self):
        return (
            round(self.energy_storage / -self.power_active, 5)
            if self.power_active < 0
            else float("inf")
        )

    @property
    def heat_time(self):
        return (
            round(self.heat_storage / self.heat_active, 5)
            if self.heat_active > 0
            else float("inf")
        )


class Module:
    def __init__(self, size, weight, techlevel, details=None):
        self.size = size
        self.weight = weight
        try:
            self.techlevel = int(techlevel)
        except:
            self.techlevel = TECHLEVELS.index(techlevel)
        self.modes = details.get("Modes", [])
        self.special = {} if details is None else details


SBiped = [
    Module(
        1,
        1,
        "L",
        details={
            "Modes": {
                "Offline": {"Energy": 0, "Heat": 0, "Speed": 0},
                "Passive": {"Energy": -0.1, "Heat": 0.1, "Speed": 3},
                "Active": {"Energy": -0.8, "Heat": 0.5, "Speed": 30},
            },
            "Propulsion": 1,
        },
    )
]

FBiped = [
    Module(
        1,
        1,
        "M",
        details={
            "Modes": {
                "Offline": {"Energy": 0, "Heat": 0, "Speed": 0},
                "Passive": {"Energy": -0.3, "Heat": 0.1, "Speed": 5},
                "Active": {"Energy": -1.2, "Heat": 0.5, "Speed": 35},
            },
            "Propulsion": 1,
            "Type": "Movement",
        },
    )
]

PEM = [
    Module(
        1,
        1,
        "M",
        details={
            "Modes": {
                "Offline": {"Energy": 0, "Heat": 0},
                "Passive": {"Energy": 0.5, "Heat": 0.1},
                "Active": {"Energy": 3.5, "Heat": 0.5},
            },
            "Type": "Energy",
        },
    )
]

Autocannon = [
    Module(
        3,
        3,
        "M",
        details={
            "Modes": {
                "Offline": {"Energy": 0, "Heat": 0},
                "Singlefire": {
                    "Energy": 0,
                    "Heat": 2,
                    "Ammo": -0.01,
                    "Damage": 2,
                    "Cooldown": 1,
                },
                "Burstfire": {
                    "Energy": 1,
                    "Heat": 5,
                    "Ammo": -0.15,
                    "Damage": 4,
                    "Cooldown": 0,
                },
            },
            "Type": "Weapon",
        },
    )
]

Vent = [
    Module(
        1,
        1,
        "L",
        details={
            "Modes": {
                "Offline": {"Energy": 0, "Heat": 0},
                "Passive": {"Energy": -0.2, "Heat": -1},
                "Active": {"Energy": -0.8, "Heat": -6},
                "HeatStorage": 3,
            },
            "Type": "Heat",
        },
    )
]

Sink = [
    Module(
        1,
        1,
        "M",
        details={
            "HeatAt0": {"Energy": 0, "Heat": -0.4},
            "HeatAt15": {"Energy": 0, "Heat": -0.4},
            "HeatAt25": {"Energy": 0, "Heat": -0.2},
            "HeatStorage": 25,
            "Type": "Heat",
        },
    )
]

Cargo = [Module(1, 1, "B", details={"CargoMax": 10})]

BShield_C = [
    Module(
        1,
        1,
        "L",
        details={
            "Modes": {
                "Offline": {"Energy": 0, "Heat": 0},
                "Charging": {"Energy": -0.5, "Heat": 0, "Reboot": "C - R"},
                "Active": {
                    "Energy": -0.2,
                    "Heat": 0,
                    "HeatOnHit": 3,
                    "Shield": 1,
                    "Overwhelm": ["dampen", "5H", "disable"],
                },
                "Coldboot": "5r",
            },
            "Coverage": "12+C*8",
            "Dedication": "C",
            "Type": "Shield",
        },
    )
]

Armor = [
    Module(
        1,
        1,
        "L",
        details={"Coverage": "M*12", "Armor": "4", "HP": "sqrt(M)*2", "Type": "Armor"},
    )
]


def maxspeed(m, p, air_coeff, ground_coeff, base_loss, significant_digits=3) -> int:
    d = m * ground_coeff / 100 * 9.81  # kg * 1 * m/s2  ; weight based friction
    old, vel, airdrag = 0, 10, p / 100  # approximation seeds
    p -= base_loss
    while abs(old - vel) > 1 / 10 ** significant_digits:
        old = vel
        airdrag = (airdrag + (0.5 * air_coeff * 1.225) * vel ** 2) / 2
        vel = p / (airdrag + d)
    return vel


def movementenergyneed(movementsystem, stats):
    stats = stats[0]
    return int(mechdata.movementsystems()[movementsystem][0]) * stats[0] * stats[1] / 100


def movementenergysystempercentages(choices):
    out = {}
    for mname, mstats in choices.items():
        need = movementenergyneed(mname, mstats)
        out[mname] = {"E needed": need, "stats": mstats}
        out[mname]["options"] = {}
        for name, stats in mechdata.energysytems().items():
            if "@" in stats[0]:
                stats[0] = stats[0].split("@")[1]
            out[mname]["options"][name] = round(need / float(stats[0]), 4)
    return out


def movementspeed(movement, size, energy):
    mov = mechdata.movementsystems()[movement]
    piloting, tonnage = sizes()[str(size)]
    tonnage = float(tonnage)
    scale = float(energy) / float(mov[0])
    power = float(mov[3]) * scale
    return maxspeed(
        tonnage * 1e3, power * 1e3, float(mov[2]) * int(size), float(mov[1]) * tonnage, 0
    )


def movementsystempercentages(target_speed, mechsize):
    speeds = {}
    piloting, tonnage = sizes()[str(mechsize)] if mechsize else ("", 0.0001)
    tonnage = float(tonnage)

    for name, stats in mechdata.movementsystems().items():
        p = int(stats[3]) * 1000
        air = float(stats[2]) * mechsize if mechsize else 1
        ground = float(stats[1]) * tonnage

        speed = sorted(
            [
                (
                    percent,
                    maxspeed(
                        tonnage * 1000, p * percent * tonnage / 100, air, ground, 0
                    ),
                )
                for percent in range(0, 101)
            ],
            key=lambda x: abs(target_speed - x[1]),
        )[0]

        speeds[name] = speeds.get(name, []) + [(tonnage, speed[0])]
    return speeds


def graphspeeds(goal):
    speeds = {}
    for i in range(16):
        for k, v in movementsystempercentages(goal, i).items():
            speeds[k] = speeds.get(k, []) + v

    for name, data in speeds.items():
        plt.plot([d[0] for d in data], [d[1] for d in data], label=name)
        plt.legend()
    plt.show()
    for name, data in speeds.items():
        plt.plot([d[1] for d in data], label=name)
        plt.legend()
    plt.show()


if __name__ == "__main__":
    graphspeeds(20)
    exit(0)

    mech = Mech(
        SBiped * 9 + PEM * 4 + Vent * 1 + Sink + BShield_C * 6 + Cargo * 12 + Autocannon
    )

    print(
        """modules: {0}
    sizeclass: {1} @ {techlevel}
    Credits: {2}
    Power A: {3} ({energyduration} rounds until energy is drained)
    Power P: {4}
    Heat A: {5} ({heatduration} rounds until overheat)
    Heat P: {6}
    Speed%: {7}""".format(
            mech.moduleamt,
            mech.sizeclass,
            mech.modulecosts,
            mech.power_active,
            mech.power_idle,
            mech.heat_active,
            mech.heat_idle,
            mech.speedpercent,
            energyduration=mech.energy_time,
            heatduration=mech.heat_time,
            techlevel=mech.techlevel,
        )
    )
