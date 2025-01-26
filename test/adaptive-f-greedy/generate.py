import yaml
import os
import sys
import os.path
import textwrap

def get_aste_config(config, participant):
    
    mesh_name = config['coarse-mesh'] if participant=="A" else config['fine-mesh']
    read_data = "\"Data\"" if participant=="B" else ""
    write_data = "\"Data\"" if participant=="A" else ""
     
    return textwrap.dedent(f"""
    {{
        "participant": "{participant}",
        "startdt": "1",
        "meshes": [
            {{
                "mesh": "{participant}-Mesh",
                "meshfileprefix": "{config['run-location']}/testcase/{mesh_name}_eval",
                "read-data": {{
                    "scalar": [{read_data}]
                }},
                "write-data": {{
                    "scalar": [{write_data}]
                }}
            }}
        ],
        "precice-config": "{config['run-location']}/testcase/precice-config.xml"
    }}
    """)
    
def get_precice_config(config):
    
    return textwrap.dedent(f"""    <?xml version="1.0" encoding="UTF-8" ?>
    <precice-configuration>
    <log enabled="0" />

    <profiling mode="all"  flush-every="0" synchronize="true"/>

    <data:scalar name="Data"/>

    <mesh name="A-Mesh" dimensions="3">
        <use-data name="Data" />
    </mesh>

    <mesh name="B-Mesh" dimensions="3">
        <use-data name="Data" />
    </mesh>

    <m2n:sockets acceptor="A" connector="B" exchange-directory="." />

    <participant name="A">
        <provide-mesh name="A-Mesh" />
        <write-data name="Data" mesh="A-Mesh" />
    </participant>

    <participant name="B">
        <receive-mesh name="A-Mesh" from="A" />
        <provide-mesh name="B-Mesh" />
        <read-data name="Data" mesh="B-Mesh" />
        <mapping:rbf-greedy greedy-type="{config['greedy-type']}" solver-rtol="{config['solver-rtol']}" constraint="{config['constraint']}" direction="read" from="A-Mesh" to="B-Mesh" polynomial="{config['polynomial']}">
        <basis-function:{config['basis-function']} support-radius="{config['support-radius']}" />
        </mapping:rbf-greedy>
    </participant>

    <coupling-scheme:serial-explicit>
        <participants first="A" second="B" />
        <max-time-windows value="{config['time-steps']}"/>
        <time-window-size value="{config['time-step-size']}" />
        <exchange data="Data" mesh="A-Mesh" from="A" to="B" />
    </coupling-scheme:serial-explicit>
    </precice-configuration>
    """)


def get_run_file(config):
    return textwrap.dedent(f"""
    set -e

    TEST_NAME="adaptive-f-greedy"

    TIME_STEPS={config['time-steps']}
    TIME_STEP_SIZE={config['time-step-size']}
    COARSE_MESH="{config['coarse-mesh']}"
    FINE_MESH="{config['fine-mesh']}"

    export ROOT_LOCATION="$(pwd)"
    RUN_LOCATION="{config['run-location']}"
    TEST_LOCATION="{config['run-location']}/testcase"
    ASTE_SRC="{config['aste-location']}/src"
    ASTE_BUILD="{config['aste-location']}/build"
    MAPPING_TESTER="{config['aste-location']}/tools/mapping-tester"

    echo ""
    echo "[TEST] precice-aste-evaluate"
    echo ""

    cd "${{RUN_LOCATION}}"
    python3 "${{ASTE_SRC}}/precice-aste-evaluate" -m "${{ROOT_LOCATION}}/meshes/${{COARSE_MESH}}.vtk" -f "{config['test-function']}" -d "Data" -o "${{COARSE_MESH}}_eval.vtk" -dir "${{TEST_LOCATION}}" --time_steps $TIME_STEPS --time_step_size $TIME_STEP_SIZE
    python3 "${{ASTE_SRC}}/precice-aste-evaluate" -m "${{ROOT_LOCATION}}/meshes/${{FINE_MESH}}.vtk" -f "{config['test-function']}" -d "Data" -o "${{FINE_MESH}}_eval.vtk" -dir "${{TEST_LOCATION}}" --time_steps $TIME_STEPS --time_step_size $TIME_STEP_SIZE

    echo ""
    echo "[TEST] precice-aste-run"
    echo ""

    cd "${{ASTE_BUILD}}"
    ./precice-aste-run --aste-config "${{TEST_LOCATION}}/aste-config-A.json" & ./precice-aste-run --aste-config "${{TEST_LOCATION}}/aste-config-B.json"
    mv -f "${{ASTE_BUILD}}/precice-profiling" "${{TEST_LOCATION}}/precice-profiling"

    echo ""
    echo "[TEST] precice-aste-evaluate"
    echo ""

    cd "${{TEST_LOCATION}}"
    python3 "${{ASTE_SRC}}/precice-aste-evaluate" -m "${{TEST_LOCATION}}/${{FINE_MESH}}_eval.vtk" -f "{config['test-function']}" -d difference --diffdata "Data" --diff --time_steps $TIME_STEPS --time_step_size $TIME_STEP_SIZE --stats

    echo ""
    echo "[TEST] precice-profiling"
    echo ""

    cd "${{TEST_LOCATION}}/precice-profiling"
    precice-profiling merge . .
    precice-profiling trace
    precice-profiling export

    mkdir -p ../../data
    mv profiling.csv ../../data/profiling.csv
    mv trace.json ../../data/treace.json
    mv ../${{FINE_MESH}}_eval.stats.csv ../../data/statistics.csv
    """)


def main():
    
    if len(sys.argv) == 4:
        config_path = sys.argv[1]
        run_location = sys.argv[2]
        aste_location = sys.argv[3]
    else:
        raise "Expected: python3 generate.py config-path run-location aste-location"
    
    with open(config_path) as stream:
        try:
            config = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    
    config["run-location"] = os.path.abspath(run_location)
    config["aste-location"] = os.path.abspath(aste_location)
    print(f"Generating files in \"{config['run-location']}\".")
    
    with open(f'{config["run-location"]}/testcase/precice-config.xml', 'w') as file:
        file.write(get_precice_config(config))
    
    with open(f'{config["run-location"]}/testcase/aste-config-A.json', 'w') as file:
        file.write(get_aste_config(config, "A"))
        
    with open(f'{config["run-location"]}/testcase/aste-config-B.json', 'w') as file:
        file.write(get_aste_config(config, "B"))
        
    with open(f'{config["run-location"]}/testcase/run.sh', 'w') as file:
        file.write(get_run_file(config))
    
if __name__ == "__main__":
    main()