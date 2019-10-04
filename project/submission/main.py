import sys
import numpy as np

"""
100 CT classification Elevation,Aspect,Slope,Horizontal_Distance_To_Hydrology, [...], Cover_Type 
2596,51,3,258,0,510,221,232,148,6279,1,0,0,0,0,0,0,0,0,0, [...], 5
"""


def main():
    line_count = int(sys.argv[1])
    dataset_name = sys.argv[2]
    run_type = sys.argv[3]
    col_names = sys.argv[4:]

    # Process the column names to fix the commas
    col_names = " ".join(col_names).replace(",", "").replace("  ", " ").split(" ")

    print("line_count", line_count)
    assert(line_count >= 1)

    print("dataset_name", dataset_name)
    assert(dataset_name in ["CT", "PD"])

    print("run_type", run_type)
    assert(run_type in ["preprocessing", "unsupervised", "classification"])

    print("col_names", col_names)

    for i in range(line_count):
        line = sys.stdin.readline()

if __name__ == '__main__':
   main()