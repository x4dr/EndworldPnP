from abc import ABC, abstractmethod
from typing import Iterable, List

from serve.mechdata import mech_json_data


class MechSystem(ABC):
    _data = mech_json_data()

    @property
    def data(self) -> dict:
        return self._data[self.systemtype()]

    def hardpointusage(self, total) -> float:
        if self.hardpoints.endswith("%"):
            return total * float(self.hardpoints[:-1]) / 100
        else:
            return float(self.hardpoints)

    @classmethod
    @abstractmethod
    def systemtype(cls) -> str:
        return "mechsystem"

    @classmethod
    @abstractmethod
    def systemproperties(cls) -> List[str]:
        pass

    # noinspection PyUnusedLocal
    @abstractmethod
    def __init__(self, name: str, properties: Iterable[str], scale: float = 1.0):
        self.name = name
        self.amount = 1
        self.config = {}
        self.hardpoints = "0"

    @abstractmethod
    def scale(self, amount: float) -> None:
        pass

    @abstractmethod
    def as_json(self) -> dict:
        return {"systemtype": self.systemtype(), "name": self.name}

    @staticmethod
    def from_json(cls, json: dict):
        if json["systemtype"] != cls.systemtype():
            raise ValueError(f"{json}\n does not describe a {cls.systemtype()}system")
        name = json["name"]
        properties = [json[x] for x in cls.systemproperties()]
        system = cls(name, properties)
        if "amount" in json.keys():
            system.amount = json["amount"]
        return system


class EnergySystem(MechSystem):
    @classmethod
    def systemproperties(cls) -> List[str]:
        return ["energy", "heat", "fuel", "efficiency"]

    @classmethod
    def systemtype(cls) -> str:
        return "energy"

    def __init__(self, name, properties=None, scale=1.0):
        super().__init__(name, properties, scale)
        self.name = name
        if properties is None:
            properties = self.data[name]
        self.energy_per_turn = float(properties[0])
        self.heat_per_turn = float(properties[1])
        self.fuel = properties[2]
        self.efficiency = properties[3]
        self.scale(scale)

    def scale(self, amount):
        factor = amount / self.amount
        self.energy_per_turn *= factor
        self.heat_per_turn *= factor
        self.amount *= factor

    def as_json(self):
        json = super().as_json()
        json.update(
            {
                "energy": self.energy_per_turn,
                "heat": self.heat_per_turn,
                "fuel": self.fuel,
                "efficiency": self.efficiency,
                "amount": self.amount,
            }
        )
        return json


class MovementSystem(MechSystem):
    @classmethod
    def systemproperties(cls) -> List[str]:
        return ["energy", "groundcoefficient", "area", "power", "hardpoints", "notes"]

    @classmethod
    def systemtype(cls) -> str:
        return "movement"

    def __init__(self, name, properties=None, scale=1.0):
        super().__init__(name, properties, scale)
        if properties is None:
            properties = self.data[name]
        self.energy_per_turn = float(properties[0])
        self.ground_coefficient = float(properties[1])
        self.area_per_sector = float(properties[2])
        self.power = float(properties[3])
        self.hardpoints = properties[4]
        self.notes = properties[5]
        self.scale(scale)

    def scale(self, amount):
        factor = amount / self.amount
        self.energy_per_turn *= factor
        self.ground_coefficient *= factor
        self.power *= factor
        self.amount *= factor

    def as_json(self):
        json = super().as_json()
        json.update(
            {
                "energy": self.energy_per_turn,
                "groundcoefficient": self.ground_coefficient,
                "area": self.area_per_sector,
                "power": self.power,
                "hardpoints": self.hardpoints,
                "notes": self.notes,
                "amount": self.amount,
            }
        )
        return json


class HeatSystem(MechSystem):
    @classmethod
    def systemproperties(cls) -> List[str]:
        return ["energy", "cooling", "capacity", "hardpoints"]

    @classmethod
    def systemtype(cls) -> str:
        return "heat"

    def __init__(self, name, properties=None, scale=1.0):
        super().__init__(name, properties, scale)
        if properties is None:
            properties = self.data[name]
        if properties[0].strip().endswith("E/r"):
            self.energy_per_turn = float(properties[0].strip()[:-3])
            self.active = None
        elif properties[0].strip().endswith("E"):
            self.energy_per_turn = 0
            self.active = float(properties[0].strip()[:-1])
        elif properties[0].strip() == "0":
            self.energy_per_turn = 0
            self.active = None
        else:
            raise ValueError(
                f"{properties[0]} is not a valid Energy usage for a Heatsystem!"
            )
        cooling = properties[1]
        if ";" in cooling:
            self.cooling_passive, self.cooling_active = cooling.split(";")
        else:
            self.cooling_passive = cooling
            self.cooling_active = cooling
        self.capacity = float(properties[2])
        if properties[3].endswith("+"):
            self.config["additional hardpoints"] = 0
            self.hardpoints = properties[3][:-1]
        else:
            self.hardpoints = int(properties[3].strip() or 0)

    def scale(self, amount):
        pass

    def as_json(self):
        json = super().as_json()
        if self.cooling_active == self.cooling_passive:
            cooling = self.cooling_active
        else:
            cooling = self.cooling_passive + ";" + self.cooling_active
        json.update(
            {
                "energy": self.energy_per_turn,
                "cooling": cooling,
                "capacity": self.capacity,
                "hardpoints": self.hardpoints,
                "config": self.config,
                "amount": self.amount,
            }
        )
        return json

    @staticmethod
    def from_json(cls, json: dict):
        system = super().from_json(cls, json)
        if "config" in json.keys():
            system["config"] = json["config"]
        return system


class SealSystem(MechSystem):
    @classmethod
    def systemproperties(cls) -> List[str]:
        return ["level", "resistance", "modified_cost"]

    @classmethod
    def systemtype(cls) -> str:
        return "seal"

    def __init__(self, name, properties=None, scale=1.0):
        super().__init__(name, properties, scale)
        if properties is None:
            properties = self.data[name]
        self.level = int(properties[0])
        self.resistance = int(properties[1])
        self.modified_cost = int(properties[2])

    def scale(self, amount):
        self.amount = amount
        pass

    def as_json(self):
        json = super().as_json()
        json.update(
            {
                "level": self.level,
                "resistance": self.resistance,
                "modified_cost": self.modified_cost,
                "amount": self.amount,
            }
        )
        return json


class DefenseSystem(MechSystem):
    def as_json(self):
        json = super().as_json()
        json.update(
            {
                "protection": self.protection,
                "weight": self.weight,
                "cost": self.cost,
                "failure": self.failure,
                "reboot": self.reboot,
                "coldboot": self.coldboot,
                "amount": self.amount,
            }
        )
        return json

    @classmethod
    def systemproperties(cls) -> List[str]:
        return ["protection", "weight", "cost", "failure", "reboot", "coldboot"]

    @classmethod
    def systemtype(cls) -> str:
        return "defense"

    def __init__(self, name, properties=None, scale=1.0):
        super().__init__(name, properties, scale)
        if properties is None:
            properties = self.data[name]
        self.protection = properties[0]
        self.weight = float(properties[1])
        self.cost = properties[2]
        self.failure = properties[3]
        self.reboot = properties[4]
        self.coldboot = properties[5]

    def scale(self, amount):
        pass


class ArmorSystem(MechSystem):
    @classmethod
    def systemproperties(cls) -> List[str]:
        return ["level", "weight", "failuremode"]

    def as_json(self) -> dict:
        json = super().as_json()
        json.update(
            {
                "level": self.level,
                "weight": self.weight,
                "failuremode": self.failuremode,
                "amount": self.amount,
            }
        )
        return json

    @classmethod
    def systemtype(cls) -> str:
        return "armor"

    def __init__(self, name, properties=None, scale=1.0):
        super().__init__(name, properties, scale)
        if properties is None:
            properties = self.data[name]
        self.level = properties[0]
        self.weight = properties[1]
        self.failuremode = properties[2]

    def scale(self, amount):
        self.amount = amount


class WeaponSystem(MechSystem):
    @classmethod
    def systemproperties(cls) -> List[str]:
        return ["damage", "ranges", "costs", "weight"]

    def as_json(self) -> dict:
        pass

    @classmethod
    def systemtype(cls) -> str:
        return "weapon"

    def __init__(self, name, properties=None, scale=1.0):
        super().__init__(name, properties, scale)
        if properties is None:
            properties = self.data[name]
        self.damage = properties[0]
        self.ranges = properties[1]
        self.costs = properties[2]
        self.weight = properties[3]

    def scale(self, amount):
        Exception("Weapons do not scale!")


class Mech:
    energysystems: List[EnergySystem]
    movementsystems: List[MovementSystem]
    heatsystems: List[HeatSystem]
    sealsystems: List[SealSystem]
    defensesystems: List[DefenseSystem]
    armorsystems: List[ArmorSystem]
    weaponsystems: List[WeaponSystem]

    def __init__(self, mech: dict):
        self.hardpoints = 0
        self.energysystems = []
        self.movementsystems = []
        self.heatsystems = []
        self.sealsystems = []
        self.defensesystems = []
        self.armorsystems = []
        self.weaponsystems = []
        self.notes = ""

        for system, data in mech.items():
            if system == "size":
                self.hardpoints = mech[system]
                continue
            if system == "notes":
                self.notes = mech[system]
                continue

            if isinstance(data, str):  # type_name_id : amount
                systemtype, systemname, i = system.split("_")
                amount = float(data)
                self.append(systemtype, systemname, amount)

            else:  # type : [systems]
                for subsystem in data:
                    print("SUBSYSTEM UNHANDLED:", subsystem)

    def append(self, systemtype, systemname, amount):
        if systemtype == "energy":
            self.energysystems.append(EnergySystem(systemname, scale=amount))
        elif systemtype == "movement":
            self.movementsystems.append(
                MovementSystem(systemname, scale=amount)
            )
        elif systemtype == "heat":
            self.heatsystems.append(HeatSystem(systemname, scale=amount))
        elif systemtype == "seal":
            self.sealsystems.append(SealSystem(systemname, scale=amount))
        elif systemtype == "defense":
            self.defensesystems.append(DefenseSystem(systemname, scale=amount))
        elif systemtype == "armor":
            self.armorsystems.append(ArmorSystem(systemname, scale=amount))
        elif systemtype == "weapon":
            self.weaponsystems.append(WeaponSystem(systemname, scale=amount))

    def as_json(self):
        return {
            "energy": [e.as_json() for e in self.energysystems],
            "movement": [e.as_json() for e in self.movementsystems],
            "heat": [e.as_json() for e in self.heatsystems],
            "seal": [e.as_json() for e in self.sealsystems],
            "weapons": [e.as_json() for e in self.weaponsystems],
            "defense": [e.as_json() for e in self.defensesystems],
            "armor": [e.as_json() for e in self.armorsystems],
            "notes": self.notes,
            "size": self.hardpoints,
        }

    def from_json(self, json):
        print(json)
        print(self.hardpoints)
