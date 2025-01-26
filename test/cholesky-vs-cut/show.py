import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys
import matplotlib as mp
from matplotlib.colors import LinearSegmentedColormap
from matplotlib import colors as pltcolors
import os


preCICE_orange = "#F36221"
preCICE_lightblue = "#9ECEEC"
preCICE_blue = "#0065BD"
preCICE_green ="#A1B119"

def collect_method_stats(statistics: pd.DataFrame, method: str):
    method_selector = statistics["mapping"].str.contains(method)
    method_stats    = statistics[method_selector].copy()
    
    if method == "direct":
        return method_stats
    
    method_stats["centers-percent"] = method_stats["mapping"].str.replace(f"{method}-", "").astype(int)
    method_stats["mapping"]         = method_stats["mapping"].str.replace("-[0-9]+", "")
    method_stats.sort_values("centers-percent", inplace=True)
    
    return method_stats


def get_methods(statistics: pd.DataFrame):
    return statistics["mapping"].str.replace("-[0-9]+", "", regex=True).drop_duplicates().to_list()


def main(argv):
    run_path = "./test/cholesky-vs-cut"
    if len(argv) == 2:
        run_path = argv[1]
        
    show_PUM = False
        
    time_stats_path   = os.path.join(run_path, "statistics.csv")
    memory_stats_path = os.path.join(run_path, "memory.csv")
    
    colors = { "P-cholesky": preCICE_orange, "P-cut": preCICE_blue, "PUM": preCICE_lightblue, "direct": preCICE_green}
    
    fig = plt.figure()
    
    if os.path.isfile(time_stats_path):
    
        print()
        times_csv = pd.read_csv(time_stats_path)
        greedy_methods = get_methods(times_csv)
  
        time_axes = fig.add_subplot(111, label="time")
        time_axes.set_ylabel("time ($\mu s$)")
        time_axes.yaxis.tick_left()
        time_axes.yaxis.set_label_position('left') 
        # time_axes.xaxis.set_major_formatter(mp.ticker.PercentFormatter())
        
        for method in greedy_methods:
            method_time_stats = collect_method_stats(times_csv, method)
            if show_PUM:
                time_axes.plot(method_time_stats["relative-l2"], method_time_stats["globalTime"], marker="o", color=colors[method], linestyle="solid", label=method.replace("cut","inv-cholesky") + " (time)")
                time_axes.set_xscale("log")
                time_axes.set_yscale("log")
            elif "P-" in method:
                time_axes.plot(method_time_stats["centers-percent"], method_time_stats["globalTime"], marker="o", color=colors[method], linestyle="solid", label=method.replace("cut","inv-cholesky") + " (time)")
                
    
    else:
        print(f"\"{time_stats_path}\": no timing data found.")
        return

    
    #greedy_methods = get_methods(memory_csv)

    memory_axes = fig.add_subplot(111, label="memory", frame_on=False, sharex=time_axes)
    memory_axes.set_ylabel("memory ($MB$)")
    memory_axes.yaxis.tick_right()
    memory_axes.yaxis.set_label_position('right') 
        
    for method in greedy_methods:
  
        method_time_stats = collect_method_stats(times_csv, method)
     
        memory_column = "peakMemB"
        if os.path.isfile(memory_stats_path):
            memory_csv = pd.read_csv(memory_stats_path)
            method_mem_stats = collect_method_stats(memory_csv, method)
            method_mem_stats = pd.merge(method_time_stats, method_mem_stats, how="left", on=["mapping"]).dropna()
            memory_column = "memory"
        else:
            print("No external memory.csv found: plotting \"peakMemB\" from ASTE.")
            method_mem_stats = method_time_stats
        
        if show_PUM:
            memory_axes.plot(method_mem_stats["relative-l2"], method_mem_stats[memory_column], marker="D", color=colors[method], linestyle="dotted", label=method.replace("cut","inv-cholesky") + " (memory)")
            time_axes.set_xscale("log")
        elif "P-" in method:
            memory_axes.plot(method_mem_stats["centers-percent_x"], method_mem_stats[memory_column], marker="D", color=colors[method], linestyle="dotted", label=method.replace("cut","inv-cholesky") + " (memory)")
    
    
    time_handles, labels = time_axes.get_legend_handles_labels()
    memory_handles, labels = memory_axes.get_legend_handles_labels() # TODO: Unschön nur wenn "centers" angezeigt wird hübsch
    
    time_axes.grid(True, which="major", axis="y", color="gainsboro", linestyle="-", linewidth=0.5)
    memory_axes.grid(True, which="major", axis="y", color="gainsboro", linestyle="-", linewidth=0.5)
    time_axes.grid(True, which="major", axis="x", color="gainsboro", linestyle="-", linewidth=0.5)
    
    if show_PUM:
        time_axes.set_xlabel("Error (RMSE)")
        plt.legend(handles=time_handles+memory_handles, loc='upper right')
    else:
        time_axes.set_xlabel("used centres (\%)")
        plt.legend(handles=time_handles+memory_handles, loc='upper left')
    
    plt.gcf().set_size_inches(7.5,6)
    plt.tight_layout()
    plt.show()
    
if __name__ == "__main__":
    
    plt.rcParams.update({
        "text.usetex": True,
        "font.family": 'serif',
        "font.serif": ['Computer Modern'],
        "font.size": 15
    })
    plt.rc("legend", fontsize=11)
    main(sys.argv)