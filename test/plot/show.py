import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys
from matplotlib.colors import LinearSegmentedColormap
from matplotlib import colors as pltcolors

class Config:
    function: str      # franke, cos, eggholder
    error: str         # relative-l2
    mesh: str          # turbine, halton
    rbf: str           # gauss-45, c2-10, c2-5
    
    include_iter: bool # True, False
    repr_h: float


###### HELPERS ######

def get_grid_resolutions(config: Config):
    if config.mesh == "halton":
        return [0.168, 0.084, 0.042, 0.021, 0.0105, 0.00525, 0.002625]
    elif config.mesh == "turbine":
        return [0.03, 0.02, 0.01, 0.006, 0.004] # 0.008 (5310), 0.009 (4302) fehlt
    else:
        raise f"unknown mesh: config.mesh={config.mesh}"


def get_grid_sizes(config: Config):
    if config.mesh == "halton":
        return [9, 25, 81, 289, 1089, 4225, 16641]
    elif config.mesh == "turbine":
        return [438, 924, 3458, 9588, 21283] # 0.008 (5310), 0.009 (4302) fehlt
    else:
        raise f"unknown mesh: config.mesh={config.mesh}"


def read_greedy_values_file(config: Config):
    return pd.read_csv(f"test/plot/data/M={config.mesh}_f={config.function}_rbf={config.rbf}/greedy_values.csv").sort_values(by="mesh A", ascending=False)


def read_statistics_file(config: Config):
    return pd.read_csv(f"test/plot/data/M={config.mesh}_f={config.function}_rbf={config.rbf}/statistics.csv").sort_values(by="mesh A", ascending=False)


def set_properties(config: Config, data_field: str):
    plt.grid(True, which="major", color="gainsboro", linestyle="-", linewidth=0.5)
    plt.rc("legend",fontsize="small")
    
    # x-Achse
    plt.gca().xaxis.set_inverted(True)
    plt.xscale("log")
    plt.xlabel("h")
    plt.gca().set_xticks(get_grid_resolutions(config))
    if data_field == "centers":
        plt.xlabel("N")
        plt.gca().set_xticklabels(get_grid_sizes(config))
    else:
        plt.gca().set_xticklabels(get_grid_resolutions(config))
        
    # y-Achse
    ylabel = data_field
    if data_field == "relative-l2":
        ylabel = "RMSE Error"
    elif "time" in data_field.lower():
        ylabel = data_field + " (µs)"
    if data_field != "centers": 
        plt.yscale("log")
    else:
        plt.gca().set_yticks([0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1])
        plt.gca().set_yticklabels(["0%", "10%", "20%", "30%", "40%", "50%", "60%", "70%", "80%", "90%", "100%"])
    plt.ylabel(ylabel)


###### PLOTS ######

def compare_centers(config: Config):
    stats_file  = pd.read_csv(f"test/plot/data/statistics_centers.csv").sort_values(by="mesh A", ascending=False)
    greedy_file = pd.read_csv(f"test/plot/data/greedy_values_centers.csv")
    raw_stats   = pd.merge(stats_file, greedy_file, left_on="mapping", right_on="mapping", how="left")
    
    f_stats = raw_stats[raw_stats["mapping"].str.contains(f"f-greedy_")]
    p_stats = raw_stats[raw_stats["mapping"].str.contains(f"p-greedy_")]

    plt.plot(f_stats["n"], f_stats[config.error], marker="o", linestyle="none", markersize=5, color="tab:red", label=f"f-greedy")
    plt.plot(p_stats["n"], p_stats[config.error], marker="d", linestyle="none", markersize=5, color="tab:blue", label=f"P-greedy")
    
    plt.grid(True, which="both", color="gainsboro", linestyle="-", linewidth=0.5)
    plt.rc("legend",fontsize="small")
    plt.legend()
    plt.xlabel("Number of Centers (n)")
    plt.ylabel(f"{config.error} Error")
    plt.yscale("log")
    
    plt.show()
    
    
def compare_f_p(config: Config):
    stats_file  = pd.read_csv(f"test/plot/data/statistics_{config.function}.csv").sort_values(by="mesh A", ascending=False)
    greedy_file = pd.read_csv(f"test/plot/data/greedy_values_{config.function}.csv").sort_values(by="mesh A", ascending=False)
    
    color_gradiant = ["yellowgreen", "red", "tab:blue"]

    colors     = {}
    markers    = {}
    linestyles = {}
    names      = {}
    
    compare_maps  = []
    f_greedy_maps = []
    p_greedy_maps = []
    
    if config.function == "franke2d(xy)" and config.error == "median(abs)":
        f_greedy_maps = ["f-greedy_1e-6",     "f-greedy_1e-8",  "f-greedy_1e-10"]
        p_greedy_maps = ["p-greedy_1e-5.5",   "p-greedy_1e-6",   "p-greedy_1e-6.5"]
    elif config.function == "franke2d(xy)" and config.error == "relative-l2":
        f_greedy_maps = ["f-greedy_1e-5",     "f-greedy_1e-7",  "f-greedy_1e-9"]
        p_greedy_maps = ["p-greedy_1e-5.5",   "p-greedy_1e-6",   "p-greedy_1e-7"]
    else:
        print("No configuration available for this case.")
        return
    
    for i, map in enumerate(f_greedy_maps):
        colors[map] = color_gradiant[i]
        markers[map] = "d"
        linestyles[map] = "dotted"
        t = map.split("-")[4]
        names[map] = f"f² < 1e-{t}"
        
    for i, map in enumerate(p_greedy_maps):
        colors[map] = color_gradiant[i]
        markers[map] = "o"
        linestyles[map] = "solid"
        t = map.split("-")[4]
        names[map] = f"P² < 1e-{t}"
        
    plt.subplots(1, 3)
    
    for map in compare_maps + f_greedy_maps + p_greedy_maps:
        stats = stats_file[stats_file["mapping"].str.contains(f"{map}$")]
        
        plt.subplot(1, 3, 1)
        plt.plot(stats["mesh A"], stats[config.error], marker=markers[map], linestyle=linestyles[map], markersize=5, color=colors[map], label=f"{names[map]}")
        set_properties(config.error)
        
        plt.subplot(1, 3, 2)
        plt.plot(stats["mesh A"], stats["globalTime"], marker=markers[map], linestyle=linestyles[map], markersize=5, color=colors[map], label=f"{names[map]}")
        set_properties("globalTime")
    
    plt.subplot(1, 3, 3)
    for map in f_greedy_maps + p_greedy_maps:
        stats = greedy_file[greedy_file["mapping"].str.contains(f"{map}$")]
        plt.plot(stats["mesh A"], stats["n"] / stats["N"], marker=markers[map], linestyle=linestyles[map], markersize=5, color=colors[map], label=f"{names[map]}")
        set_properties("centers")
    
    plt.subplot(1, 3, 1)       
    plt.plot(stats["mesh A"], stats["mesh A"],    marker="+", markersize=4, linestyle="dotted", color="darkgray", label=f"h¹")
    plt.plot(stats["mesh A"], stats["mesh A"]**2, marker="+", markersize=4, linestyle="dotted", color="darkgray", label=f"h²")
    plt.plot(stats["mesh A"], stats["mesh A"]**3, marker="+", markersize=4, linestyle="dotted", color="darkgray", label=f"h³")
                
    plt.legend()
    plt.show()


def runtime_vs_error(config: Config):
    stats_file = read_statistics_file(config)
    greedy_file = read_greedy_values_file(config)

    methods = [["rbf-direct"]]
    colors  = {"rbf-direct": "tab:blue"  }
    markers = {"rbf-direct": "s"         }
    names   = {"rbf-direct": "rbf direct"}
    
    methods += [["nearest-neighbour"]]
    colors["nearest-neighbour"]  = "darkgrey"
    markers["nearest-neighbour"] = "s"
    names["nearest-neighbour"]   = "nearest neighbour"

    maps = stats_file[stats_file["mapping"].str.contains("pum_")]["mapping"].drop_duplicates().sort_values(key=lambda x: x.str.replace("pum_M", "").astype(float)).to_list()
    methods += [maps]
    for map in maps:
        colors[map]  = "tab:cyan"
        markers[map] = "d"
        t = map.split("_M")[1]
        names[map] = f"PUM: {t}"
    
    maps = greedy_file[greedy_file["mapping"].str.contains("p-greedy_")]["mapping"].drop_duplicates().sort_values(key=lambda x: x.str.replace("p-greedy_1e", "").astype(float)).to_list()
    methods += [maps]
    for map in maps:
        colors[map]  = "yellowgreen"
        markers[map] = "o"
        t = map.split("_")[1]
        names[map] = f"P²: {t}"
    
    maps = greedy_file[greedy_file["mapping"].str.contains("f-greedy_")]["mapping"].drop_duplicates().sort_values(key=lambda x: x.str.replace("f-greedy_1e", "").astype(float)).to_list()
    methods += [maps]
    for map in maps:
        colors[map]  = "red"
        markers[map] = "o"
        t = map.split("_")[1]
        names[map] = f"r²: {t}"
        
    stats_h = stats_file[stats_file["mesh A"] == config.repr_h].sort_values(by="mapDataTime", ascending=False)
    time_fields = ["computeMappingTime", "mapDataTime"]
    
    plt.subplots(1, len(time_fields))
    
    for i, time_field in enumerate(time_fields):
        plt.subplot(1, len(time_fields), 1 + i)
        for maps in methods:
            errors = []
            times = []
            for map in maps:
                stats = stats_h[stats_h["mapping"].str.contains(f"{map}$")]
                if len(stats) > 0:              
                    error = float(stats[config.error].iloc[0])
                    time  = float(stats[time_field].iloc[0])
                    errors.append(error)
                    times.append(time)
                    
                    plt.text(time + 0.1 * time, error, names[map], fontsize = 9)
                    plt.yscale("log")
                    plt.xscale("log")
            
            plt.plot(times, errors, marker=markers[maps[0]], linestyle=(0, (1, 2)), markersize=7, color=colors[maps[0]], label=f"{names[maps[0]]}")

        plt.xlabel(f"{time_field} (µs)")
        plt.ylabel(f"{'RMSE' if config.error == 'relative-l2' else config.error} Error")
        plt.grid(True, which="both", color="gainsboro", linestyle="-", linewidth=0.5)
    
    plt.suptitle(config.function)
    plt.show()   


def compare_methods(config: Config, fields: list):

    stats_file  = read_statistics_file(config)
    greedy_file = read_greedy_values_file(config)
    
    f_greedy_maps = greedy_file[greedy_file["mapping"].str.contains("f-greedy_")]["mapping"].drop_duplicates().sort_values(key=lambda x: x.str.replace("f-greedy_1e", "").astype(float)).to_list()
    p_greedy_maps = greedy_file[greedy_file["mapping"].str.contains("p-greedy_")]["mapping"].drop_duplicates().sort_values(key=lambda x: x.str.replace("p-greedy_1e", "").astype(float)).to_list()
    
    color_base_names = ["yellowgreen", "darkkhaki", "gold", "orange", "red", "mediumvioletred", "mediumpurple", "mediumslateblue"]
    color_base = [pltcolors.hex2color(pltcolors.cnames[color_name]) for color_name in color_base_names]
    color_map  = LinearSegmentedColormap.from_list("colormap", color_base, N=max(len(p_greedy_maps),len(f_greedy_maps)))

    colors     = {"rbf-direct": "tab:blue", "pum_M10": "tab:cyan", "pum_M100": "tab:cyan", "nearest-neighbour": "gray"   }
    markers    = {"rbf-direct": "v",        "pum_M10": "d",        "pum_M100": "d",        "nearest-neighbour": "v"      }
    linestyles = {"rbf-direct": "solid",    "pum_M10": "solid",    "pum_M100": "solid",    "nearest-neighbour": "dashed" }
    names      = {"rbf-direct": "direct",   "pum_M10": "PUM: 10",  "pum_M100": "PUM: 100", "nearest-neighbour": "nearest"}

    compare_maps  = ["rbf-direct", "pum_M10", "pum_M100", "nearest-neighbour"]
    
    
    for i, map in enumerate(f_greedy_maps):
        colors[map] = color_map(i)
        markers[map] = "o"
        linestyles[map] = "dotted"
        t = map.split("_")[-1]
        names[map] = f"r² < {t}"
        
    for i, map in enumerate(p_greedy_maps):
        colors[map] = color_map(i)
        markers[map] = "o"
        linestyles[map] = "dotted"
        t = map.split("_")[-1]
        names[map] = f"P² < {t}"
        
    n_plots = len(fields) + 1
    fig, axs = plt.subplots(2, n_plots)
    
    fig.suptitle(f"Mesh={config.mesh}, f={config.function}, $\phi$={config.rbf}")
    
    for i, data_name in enumerate([config.error] + fields):
        for j, greedy_maps in enumerate([f_greedy_maps, p_greedy_maps]):
            plt.subplot(2, n_plots, 1 + i + j*n_plots)
            for map in compare_maps + greedy_maps:
                if map in greedy_maps and data_name == "centers":
                    stats = greedy_file[greedy_file["mapping"].str.contains(f"{map}$")]
                    plt.plot(stats["mesh A"], stats["n"] / stats["N"], marker=markers[map], linestyle=linestyles[map], markersize=5, color=colors[map], label=f"{names[map]}")
                elif data_name != "centers":
                    stats = stats_file[stats_file["mapping"].str.contains(f"{map}$")]
                    plt.plot(stats["mesh A"], stats[data_name], marker=markers[map], linestyle=linestyles[map], markersize=5, color=colors[map], label=f"{names[map]}")
                set_properties(config, data_name)
            
            if data_name == config.error:
                plt.plot(stats["mesh A"], stats["mesh A"],    marker="+", markersize=4, linestyle="dotted", color="darkgray", label=f"h¹")
                plt.plot(stats["mesh A"], stats["mesh A"]**2, marker="+", markersize=4, linestyle="dotted", color="darkgray", label=f"h²")
                plt.plot(stats["mesh A"], stats["mesh A"]**3, marker="+", markersize=4, linestyle="dotted", color="darkgray", label=f"h³")
            if j == len([f_greedy_maps, p_greedy_maps]) - 1:
                f_handles, labels = fig.axes[0].get_legend_handles_labels()
                p_handles, labels = fig.axes[j*n_plots+1].get_legend_handles_labels() # TODO: Unschön nur wenn "centers" angezeigt wird hübsch
                fig.legend(handles=f_handles+p_handles, loc='outside upper right')
        
    plt.show()
    
    




def main(argv):
    
    plt.rcParams.update({
        "text.usetex": True,
        "font.family": 'serif',
        "font.serif": ['Computer Modern'],
        "font.size": 12
    })
    
    config = Config()
    
    # compare_methods
    config.function = "franke3d" # franke, eggholder, easom
    config.error    = "relative-l2"   # median(abs), relative-l2
    config.rbf      = "c2-5"
    config.mesh     = "turbine"
    
    # runtime_vs_error
    config.include_iter = False
    config.repr_h = 0.008
    
    compare_methods(config, ["centers", "computeMappingTime", "mapDataTime"])
    runtime_vs_error(config)
    
    

if __name__ == "__main__":
   main(sys.argv)