import polars as pl
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mp
import sys
import json
import yaml
import os

def parse_greedy_data_json(df_row):
    data = json.loads(df_row["data"].replace("\'", "\""))
    return { "N": data["inSize"], "n": data["basisSize"] }
    
    
def set_properties(label):
    plt.grid(True, which="major", color="gainsboro", linestyle="-", linewidth=0.5)
    plt.ylabel(label)
    plt.tick_params('x', labelbottom=False)
    if label == "µs":
        plt.grid(True, which="both", color="gainsboro", linestyle="-", linewidth=0.5)
        plt.yscale("log")
    if label == "centers":
        plt.gca().yaxis.set_major_formatter(mp.ticker.PercentFormatter())
        


def combine_input_files(events_csv, statistics_csv, plot_info, print_details=False):
        
    if print_details:
        pd.set_option('display.max_rows', None)
        row_selector = (events_csv["participant"] == "B") & events_csv["event"].str.contains("map.f-greedy.(solve|update)", regex=True)
        events = events_csv[row_selector]
        print(events[["event", "duration"]])
    
    row_selector = (events_csv["participant"] == "B") & events_csv["event"].str.contains("map.f-greedy.mapData")
    events = events_csv[row_selector]
    
    applied_df = events.apply(parse_greedy_data_json, axis='columns', result_type='expand')
    statistics = pd.concat([events, applied_df], axis='columns')
    statistics = statistics.reset_index()
    statistics["relative-l2"] = list(statistics_csv["relative-l2"])
    statistics = statistics.drop([len(statistics)-1], axis=0) # letzter Zeitschritt aus irgendeinem Grund verschoben
    statistics["t"] = (statistics.index.astype(int) + 1) * plot_info['time-step-size']
    
    if print_details:
        print(statistics[["t", "n", "N", "duration", "relative-l2"]])
    
    return statistics



def show_statistics(statistics, label, linestyle, marker):
    ax1 = plt.subplot(3, 1, 1)
    plt.plot(statistics["t"], statistics["duration"], marker=marker, markersize=4, linestyle=linestyle, label=label)
    set_properties("µs")

    plt.subplot(3, 1, 2, sharex=ax1)
    plt.plot(statistics["t"], (statistics["n"] / statistics["N"]) * 100, marker=marker, markersize=4, linestyle=linestyle, label=label)
    set_properties("centers")
                
    plt.subplot(3, 1, 3, sharex=ax1)
    plt.plot(statistics["t"], statistics["relative-l2"], marker=marker, linestyle=linestyle, markersize=4, label=label)
    set_properties("RMSE Error")
                
    ax1.set_xticks(statistics["t"])
    plt.tick_params('x', labelbottom=True)
                
    plt.xlabel("t")
    
    average_duration = np.average(statistics["duration"])
    average_error = np.average(statistics["relative-l2"])
    print(f"   average duration = {average_duration}")
    print(f"   average error    = {average_error}")


def load_statistics(case_path, plot_info):
    events_path     = os.path.join(case_path, "profiling.csv")
    statistics_path = os.path.join(case_path, "statistics.csv")
        
    if not (os.path.isfile(events_path) or os.path.isfile(statistics_path)):
        print(f"\"{os.path.isfile(events_path)}\" or \"{os.path.isfile(statistics_path)}\": no data found, skipping")
        return None
        
    events_csv     = pd.read_csv(events_path)
    statistics_csv = pd.read_csv(statistics_path)
                
    return combine_input_files(events_csv, statistics_csv, plot_info, print_details=False)


def load_yaml_info(info_yaml_path):
    if not os.path.isfile(info_yaml_path):
        print(f"\"{info_yaml_path}\": Plotting information not found.")
        return None
    with open(info_yaml_path) as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(f"\"{info_yaml_path}\": YAML Error: \n {exc}")
            return None


def main(argv):
    run_path = "./test/adaptive-f-greedy"
    if len(argv) == 2:
        run_path = argv[1]
        
    
    plot_name = "cholesky-compare-all"
    
    
    plot_path = os.path.join(run_path, "data", plot_name)
    plot_info = load_yaml_info(os.path.join(plot_path, "plot-info.yaml"))
    
    linestyles = ["solid", "dashed", "dotted", "dashdot"]
    markers = ["o", "v", "d", "h", "s", "P"]
        
    if plot_info is not None:
        
        plt.suptitle(f"{plot_name}: Mesh={plot_info['mesh']}, f={plot_info['test-function']}, φ={plot_info['basis-function']} (ρ = {plot_info['support-radius']}), {plot_info['additional-info']}")
        
        i = 0
        plot_path = os.path.join(run_path, "data", plot_name)
        case_dirs = os.listdir(plot_path)
        case_dirs.sort()
        
        for case_dir in case_dirs:
            case_path = os.path.join(plot_path, case_dir)
    
            if os.path.isdir(case_path) and not case_dir.startswith("."):
                print(f"Found case: \"{case_dir}\"")
                sub_case_dirs = os.listdir(case_path)
                sub_case_dirs.sort()
                
                for sub_case_dir in sub_case_dirs:
                    sub_case_path = os.path.join(case_path, sub_case_dir)
                    
                    if os.path.isdir(sub_case_path) and not sub_case_dir.startswith("."):
                        print(f" > sub-case: \"{sub_case_dir}\"")
                        
                        statistics = load_statistics(sub_case_path, plot_info)
                        if statistics is None:
                            continue
                        
                        show_statistics(statistics, f"{case_dir}: {sub_case_dir}", linestyles[i % len(linestyles)], markers[i % len(markers)])
                i += 1
            
                for j in range(1, 4):
                    ax = plt.subplot(3, 1, j)
                    ax.set_prop_cycle(None)

        handles, labels = plt.gca().get_legend_handles_labels()
        plt.gcf().legend(handles, labels, loc='outside lower center')
        
    else:
        print(f"Showing results at default path.")
        
        case_path = os.path.join(run_path, "data")
        plot_info = load_yaml_info(os.path.join(run_path, "config.yaml"))
        
        statistics = load_statistics(case_path, plot_info)
        if statistics is None:
            print(f"\"{case_path}\": no data found, skipping")
            return
        
        show_statistics(statistics, "Latest", "solid", "o")
        plt.suptitle("Latest")
        
    plt.show()
    
if __name__ == "__main__":
   main(sys.argv)