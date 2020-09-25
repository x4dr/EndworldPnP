import functools
from pathlib import Path


def get(res) -> str:
    with open(Path(__file__).parent.parent / Path(res)) as data:
        return data.read()


def getsystems(search):
    systems = get("mecha/systems.tex").split(r"\subsection")
    return [x for x in systems if f"{{{search}}}" in x][0]


def gettable(inp: str):
    out = []
    table = 0
    while inp:
        line, lineend, inp = inp.partition("\n")
        line = line.strip().replace(r"\%", "%")
        if not line.strip():
            continue
        if line.startswith(r"\begin{tabular}"):
            if table:
                raise Exception("no nested table support: " + line)
            line = line[15:]
            line, _, _ = line.partition("}")
            line = line.replace("{", "").replace("|", "")
            if not all(x in "clr" for x in line):
                raise Exception("unexpected in table def: " + line)
            table = len(line)
            continue
        if line.lstrip("\\").startswith(r"end{tabular}"):
            if table:
                table = 0
                continue
            raise Exception("no nested table support: " + str(out) + line)
        if table:
            if line.startswith(r"\hline"):
                continue
            while inp and line.count("&") < table - 1:
                nex, nl, inp = inp.partition("\n")
                line += nex + nl
            if line.endswith(r"\\"):
                line = line[:-2] + "\n"
            out.append([x.strip() for x in line.split("&")])
    return out


def energysytems():
    return {x[0]: x[1:] for x in gettable(getsystems("Energy Systems"))[1:]}


def movementsystems():
    return {x[0]: x[1:] for x in gettable(getsystems("Movement Systems"))[1:]}


def heatsystems():
    return {x[0]: x[1:] for x in gettable(getsystems("Heat Systems"))[1:]}


def sealsystems():
    return {x[0]: x[1:] for x in gettable(getsystems("Sealsystems"))[1:]}


def weaponsystems():
    return {x[0]: x[1:] for x in gettable(getsystems("Weapons"))[1:]}


def defensesystems():
    return {x[0]: x[1:] for x in gettable(getsystems("Defensesystems"))[1:]}


def armor():
    return {x[0]: x[1:] for x in gettable(getsystems("Armor"))[1:]}


@functools.lru_cache()
def mech_json_data():
    return {
        "energy": energysytems(),
        "movement": movementsystems(),
        "heat": heatsystems(),
        "seal": sealsystems(),
        "weapons": weaponsystems(),
        "defense": defensesystems(),
        "armor": armor(),
    }


def sizes():
    search = [x for x in get("mecha/mechs.tex").split(r"\section") if "{Sizes}" in x][0]
    return {x[0]: x[1:] for x in gettable(search)[1:]}
