"""Reads the output of NuGet benchmark, calculates new data points 
(relative duration) and appends data to csv file
Usage:
    process_results.py results.csv data.csv
"""

from pathlib import Path
import sys
import os
import pandas as pd

def read_results(csv_path: str) -> pd.DataFrame:
    """Read results"""
    # osName = re.search(r"results\_(.+)\.csv", csvPath).groups(1)[0]
    solution_name = Path(csv_path).stem

    data_from_file = pd.read_csv(csv_path)
    n_rows = int(len(data_from_file) / 2)

    duration = [data_from_file["Total Time (seconds)"][i + n_rows] for i in range(0, n_rows)]
    base_duration = [data_from_file["Total Time (seconds)"][i] for i in range(0, n_rows)]

    return pd.DataFrame(
        {
            "version": [data_from_file["Client Version"][i + n_rows] for i in range(0, n_rows)],
            "base version": [data_from_file["Client Version"][i] for i in range(0, n_rows)],
            "scenario": [data_from_file["Scenario Name"][i + n_rows] for i in range(0, n_rows)],
            "solution": [solution_name for i in range(0, n_rows)],
            # 'os': [osName for i in range(0, nRows)],
            # 'timestamp': [datetime.fromisoformat(df['Test Run ID'][i + nRows])
            # + timedelta(seconds=i) for i in range(0, nRows)],
            "timestamp": [data_from_file["Test Run ID"][i + n_rows] for i in range(0, n_rows)],
            "duration": duration,
            "base duration": base_duration,
            "relative duration": [
                duration[i] / base_duration[i] * 100 for i in range(0, n_rows)
            ],
        }
    )

if __name__ == "__main__":
    input_csv_path = sys.argv[1]
    output_csv_path = sys.argv[2]
    df = read_results(input_csv_path)
    df.to_csv(
        output_csv_path,
        mode="a",
        index=None,
        header=not os.path.exists(output_csv_path),
    )
