import re

import pandas as pd
import io


movement_systems_md = """
| name   | energy_input | thrust_output | ground_coeff |
|--------|--------------|----------------|---------------|
| legs   | 1000         | 500            | 0.015         |
| wheels | 1000         | 800            | 0.010         |
| tracks | 1000         | 600            | 0.012         |
| rails  | 1000         | 900            | 0.005         |
"""

test_configs_md = """
| name      | total_mass | power | area | move_mass | movement_type |
|-----------|------------|-------|------|-----------|----------------|
| A         | 100        | 100   | 0.5  | 5         | wheels         |
| B         | 20000      | 4000  | 4.0  | 2000      | rails          |
| C         | 5000       | 1000  | 1.0  | 100       | rails          |
"""


def clean_markdown_table(md):
    lines = [
        line
        for line in md.strip().splitlines()
        if not set(line.strip()) <= {"|", "-", " "}
    ]

    df = pd.read_csv(io.StringIO("\n".join(lines)), sep="|", engine="python").dropna(
        axis=1, how="all"
    )

    # Strip spaces from columns and all string cells
    df.columns = df.columns.str.strip()
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].astype(str).str.strip()

    return df


movement_df = clean_markdown_table(movement_systems_md)
print(movement_df)
movement_df.columns = movement_df.columns.str.strip()
movement_df.set_index("name", inplace=True)

print("\n\n\n")
test_df = clean_markdown_table(test_configs_md)
test_df.columns = test_df.columns.str.strip()
print(test_df)
print("\n\n\n")


def compute_accel(row):
    sys = movement_df.loc[row["movement_type"]]

    thrust = sys["thrust_output"]
    ground_coeff = sys["ground_coeff"]

    # simplified physics model
    thrust_term = thrust * row["move_mass"] / row["total_mass"]
    drag_term = 0.0  # you can plug in speed² * area here in real sim loop
    ground_term = row["total_mass"] * ground_coeff

    accel = thrust_term - drag_term - ground_term
    return accel


test_df["acceleration"] = test_df.apply(compute_accel, axis=1)

print(test_df[["name", "acceleration"]])
