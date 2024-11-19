"""Looks for performance regressions in the benchmark results
Usage:
    generate_alert.py data.csv regressions.txt
"""

import os
import sys
import datetime
import pandas as pd

# number of samples needed to calculate regression
SAMPLES = 10

# number of rows (days) to look back when calculating regression
ROWS = 14 * 3

# threshold in percents
THRESHOLD = 110

# quantile
QUANTILE = 0.25

def fetch_csv(csv_path: str) -> pd.DataFrame:
    """Fetch CSV"""
    return pd.read_csv(csv_path)

def get_regression(data_frame: pd.DataFrame) -> [str]:
    """Regression"""
    regression_list = []
    grouped_data = data_frame.groupby(["scenario", "solution"])
    for (_, d) in grouped_data:

        if len(d["relative duration"].values) < SAMPLES:
            continue

        # take quantile .25 from last 10 items
        result = d["relative duration"][-SAMPLES:].quantile(QUANTILE)
        if result > THRESHOLD:
            formatters = {
                'timestamp': (lambda a: a.strftime("%Y-%m-%d %H:%M:%S ")),
                'duration': (lambda a: f"{float(a):.2f}s"),
                'base duration': (lambda a: f"{float(a):.2f}s"),
                'relative duration': (lambda a: f"{float(a):.2f}%"),
            }
            columns = [
                'timestamp',
                'version',
                'duration',
                'base duration',
                'relative duration']
            header = "Scenario = " + str(d["scenario"].values[-1]) + "\n" + \
                     "Base Version = " + str(d["base version"].values[-1]) + "\n" + \
                     "Solution = " + str(d["solution"].values[-1])
            data_string = (
                d[-SAMPLES:].to_string(
                    header=True, index=False, justify="right",
                    columns=columns, formatters=formatters
                )
            )
            line_length = len(data_string.splitlines()[0])
            line = '-' * line_length
            regression_list.append('\n' + line)
            regression_list.append(header)
            regression_list.append(line)
            regression_list.append(data_string)
            regression_list.append(line)
            regression_list.append("")

    return regression_list

if __name__ == "__main__":
    data = fetch_csv(sys.argv[1])
    data["timestamp"] = pd.to_datetime(data["timestamp"])
    data = data.loc[data["scenario"] != 'warmup']

    data = data.loc[-ROWS:]

    regressions = get_regression(data)

    if regressions:
        with open(sys.argv[2], 'w', encoding='utf-8') as fp:
            fp.write('\n'.join(regressions))
    elif os.path.exists(sys.argv[2]):
        os.remove(sys.argv[2])
