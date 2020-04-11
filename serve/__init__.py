import importlib.resources
import json
import pathlib

import flask
from flask import request

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


def maxspeed(m, p, air_coeff, ground_coeff, base_loss, significant_digits=3):
    d = m * ground_coeff * 9.81  # kg * 1 * m/s2  ; weight based friction
    old, vel, airdrag = 0, 10, p / 100  # approximation seeds
    p -= base_loss
    while abs(old - vel) > 1 / 10 ** significant_digits:
        old = vel
        airdrag = (airdrag + (0.5 * air_coeff * 1.225) * vel ** 2) / 2
        vel = p / (airdrag + d)
    return vel


def get(res):
    with importlib.resources.open_text("serve", pathlib.Path(res)) as data:
        return data.read()


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
    ground_loss = float(ground_loss) / 100
    efficiency = float(efficiency) / 100
    tot_base_loss = weight  # 1watt per kilo is lost
    maxs = maxspeed(
        weight,
        power,
        crossection,
        ground_loss,
        (1 - efficiency) * power + tot_base_loss,
    )
    return {"m/s": maxs, "km/h": maxs * 3.6, "mph": maxs * 2.23694}


if __name__ == "__main__":
    app.run(debug=True)
