import importlib.resources
import json
import pathlib

import flask
from flask import request

from serve.mechacostcalc import (
    movementsystempercentages,
    movementenergysystempercentages,
    movementspeed,
)
from serve.mechdata import get, movementsystems

app = flask.Flask("KodalBroadcast")


def air_resistance(velocity, drag_coefficient, frontal_area, air_density=1.225):
    """
    :param velocity: current speed in m/s
    :param drag_coefficient: vodoo of air flowyness, unitless; for aerodynamic cars it is 0.25-0.5, cube is 1
    :param frontal_area: crossection of front, in m2
    :param air_density: 1.225 kg/m3 is standard air density at Ocean level
    :return:  (m*m/s*s) * (1) * (m2) * (kg/m3) = m4*kg /s2*m3 = m*kg/s2 = Force of Drag in Newtons
    """
    return 0.5 * drag_coefficient * frontal_area * air_density * velocity * velocity


def rolling_resistance(mass, rolling_coefficient, gravitational_force=9.81):
    """
    :param mass: total mass in kg
    :param rolling_coefficient: vodoo of rollyness:
    :param gravitational_force: local gravitational accelleration

    :return:
    """
    return mass * rolling_coefficient * gravitational_force


@app.route("/")
def root():
    return {
        "routes": {
            "/": "",
            "speed": [
                json.loads(get("speedparams.jsonschema")),
                "/<float:weight>/<float:power>/<float:crossection>/<float:ground_loss>/<float:efficiency>",
            ],
        }
    }


@app.route("/move/<movement>/<size>/<speed>")
def move(movement, size, speed):
    try:
        r = movementsystempercentages(float(speed), int(size))[movement][0]
        return {"tonnage": r[0], "percentage": r[1], "total": r[0] * r[1] / 100}
    except KeyError:
        return (
            "movement "
            + movement
            + " not found, available are: "
            + ", ".join(movementsystems().keys())
        )


@app.route("/energy/<movement>/<size>/<speed>")
def energy(movement, size, speed):
    try:
        mov = movementsystempercentages(float(speed), int(size))[movement]
        return movementenergysystempercentages({movement: mov})
    except KeyError:
        return (
            "movement "
            + movement
            + " not found, available are: "
            + ", ".join(movementsystems().keys())
        )


@app.route("/speed/<movement>/<size>/<energy>")
def mechspeed(movement, size, energy):
    try:
        maxs = movementspeed(movement, size, energy)
        return {"m/s": maxs, "km/h": maxs * 3.6, "mph": maxs * 2.23694}
    except KeyError:
        return (
            "movement "
            + movement
            + " not found, available are: "
            + ", ".join(movementsystems().keys())
        )


@app.route("/speed", methods=["GET", "POST"])
@app.route("/speed/<weight>/<power>/<crossection>/<ground_loss>/<efficiency>")
def speed(weight=None, power=None, crossection=None, ground_loss=None, efficiency=None):
    if weight is None:
        if request.method == "GET":
            return json.loads(get("speedparams.jsonschema"))
        j = request.get_json()
        if j is None:
            return {"error": "no data found"}
        weight = j["weight"]
        power = j["power"]
        crossection = j["crossection"]
        ground_loss = j["ground_loss"]
        efficiency = j["efficiency"]
    weight = float(weight)
    power = float(power)
    crossection = float(crossection)
    ground_loss = float(ground_loss)
    efficiency = float(efficiency) / 100

    maxs = maxspeed(weight, power, crossection, ground_loss, (1 - efficiency) * power,)
    return {"m/s": maxs, "km/h": maxs * 3.6, "mph": maxs * 2.23694}


if __name__ == "__main__":
    app.run(debug=True)
