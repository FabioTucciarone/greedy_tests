import polars as pl
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys
import os.path

def main(argv):

    statistics = pl.read_csv("test/shape-param/statistics.csv").sort("relative-l2")
    pl.Config.set_tbl_rows(100)
    print(statistics.select("mapping", "relative-l2", "median(abs)"))

if __name__ == "__main__":
   main(sys.argv)