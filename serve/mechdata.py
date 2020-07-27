from pathlib import Path


def get(res) -> str:
    with open(Path(__file__).parent.parent / Path(res)) as data:
        return data.read()


def getsystems(search):
    systems = get("mecha/systems.tex").split(r"\subsection")
    return [x for x in systems if f"{{{search}}}" in x][0]


def gettable(inp: str):
    out = []
    table = False
    for line in inp.splitlines(True):
        line = line.strip().replace(r"\%", "%")

        if line.startswith(r"\begin{tabular}"):
            if table:
                raise Exception("no nested table support: " + line)
            table = True
            continue
        if line.startswith(r"\end{tabular}"):
            if table:
                table = False
                continue
            raise Exception("no nested table support: " + out + line)
        if table:
            if line.startswith(r"\hline"):
                continue
            if line.endswith(r"\\"):
                line = line[:-2] + "\n"
            out.append([x.strip() for x in line.split("&")])
    return out


def energysytems():
    return {x[0]: x[1:] for x in gettable(getsystems("Energy Systems"))[1:]}


def movementsystems():
    return {x[0]: x[1:] for x in gettable(getsystems("Movement Systems"))[1:]}


def sizes():
    search = [x for x in get("mecha/mechs.tex").split(r"\section") if "{Sizes}" in x][0]
    return {x[0]: x[1:] for x in gettable(search)[1:]}
