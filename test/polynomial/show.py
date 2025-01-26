import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys
import os.path

def format_plot(ylabel, meshes):
    plt.legend()
    plt.gca().set_xticks(meshes)
    plt.gca().set_xticklabels(meshes) 
    plt.xscale("log")
    plt.xlabel("h")
    plt.xlim(0.035, 0.0035)
    plt.grid(True, which="both", color="gainsboro", linestyle="-", linewidth=0.5)
    plt.rc("legend",fontsize="small")
    plt.ylabel(ylabel)
    if ylabel != "n / N": 
        plt.yscale("log")


def main():

    case = "cos-gauss-45"
    stats_file  = pd.read_csv(f"test/polynomial/data/{case}_statistics.csv").sort_values(by="mesh A", ascending=False)
    greedy_file = pd.read_csv(f"test/polynomial/data/{case}_greedy.csv").sort_values(by="mesh A", ascending=False)
    
    tol  = ["1e-4", "1e-5", "1e-6", "1e-7"]
    poly = ["off", "sep"]
    
    meshes = [438, 0.02, 0.01, 0.008, 0.006, 0.004]
    colors = {"1e-4": "tab:green", "1e-5": "gold", "1e-6": "red", "1e-7": "tab:blue"}
    linestyles = {"off": "dashed", "sep": "solid"}
    
    for t in tol:
        for p in poly:
            mapping_type = f"poly-{p}_tol-{t}"
            stats  = stats_file[stats_file["mapping"].str.contains(mapping_type)]
            greedy = greedy_file[greedy_file["mapping"].str.contains(mapping_type)]
            
            plt.subplot(1,3,1)
            plt.plot(stats["mesh A"], greedy["n"] / greedy["N"], color=colors[t], linestyle=linestyles[p], label=mapping_type)
            format_plot("n / N", meshes)
            plt.subplot(1,3,2)
            plt.plot(stats["mesh A"], stats["mapDataTime"], color=colors[t], linestyle=linestyles[p], label=mapping_type)
            format_plot("mapDataTime", meshes)
            plt.subplot(1,3,3)
            plt.plot(stats["mesh A"], stats["relative-l2"], color=colors[t], linestyle=linestyles[p], label=mapping_type)
            format_plot("relative-l2", meshes)
            
    plt.show()
    
if __name__ == "__main__":
   main()