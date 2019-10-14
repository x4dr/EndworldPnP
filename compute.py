from collections import defaultdict
import os
import pandas
import numpy


def check(x, f, a):
    return len(x[x == f]) == (1 + a)


def process_resonance(resonance_frame):
    return resonance_frame[resonance_frame.keys()[-1]]


def main():
    resonance_complete = None
    for modifier in range(-5, 6):
        resonance = None
        df = None
        try:
            resonance = pandas.read_csv("resonance_" + str(modifier) + ".csv")
        except:
            try:
                df = pandas.read_csv("relative_occurences_" + str(modifier) + ".csv",
                                     header=None, names=["1", "2", "3", "4", "5", "sum"])
            except:
                print(str(modifier) + " unavailable!")
                continue
        if resonance is not None:
            if resonance_complete is None:
                resonance_complete = resonance
                resonance_complete.columns = ["a", "f", modifier]
            else:
                resonance_complete.insert(len(resonance_complete.keys()),
                                          modifier, resonance[resonance.keys()[-1]])
            continue
        total = 0
        print("generating: resonance_" + str(modifier) + ".csv")
        checked = defaultdict(lambda: defaultdict(int))
        for l in df.iterrows():
            rowsum = l[1][5]
            rowroll = l[1][:5]
            total += rowsum
            print(l[0] * 100 / 2002, end="%   \r")
            for amplitude in range(0, 5):
                for frequency in range(1, 11):
                    if check(rowroll, frequency, amplitude):
                        checked[frequency][amplitude] += rowsum

        print(total, "          ")
        with open(f"resonance_{modifier}.csv", "w") as f:
            f.write("a, f, " + str(total) + "\n")
            for amplitude in range(0, 5):
                for frequency in range(1, 11):
                    print(f"Amplitude {amplitude} Frequency {frequency: >2}  ={checked[frequency][amplitude]: >11}")
                    f.write(f"{amplitude}, {frequency}, {checked[frequency][amplitude]}\n")
    resonance_complete.to_csv("resonance_complete.csv")


if __name__ == "__main__":
    main()
