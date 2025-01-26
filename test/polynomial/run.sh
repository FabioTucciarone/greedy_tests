set -e -x

TEST_NAME="polynomial"

export ROOT_LOCATION="$(pwd)"
TEST_LOCATION="${ROOT_LOCATION}/test/${TEST_NAME}"

echo "[INFO] ROOT_LOCATION = \"${ROOT_LOCATION}\"  Always run from turbine_test/"

MAPPING_TESTER="${ROOT_LOCATION}/../aste/tools/mapping-tester"
TEST_CASE_LOCATION="${ROOT_LOCATION}/testcases/${TEST_NAME}/case"

export ASTE_A_MPIARGS=""
export ASTE_B_MPIARGS=""
export GRID_DISTANCE="0.01"
export CONVERGENCE_CRITERION="1e-3"

rm -rf "${TEST_CASE_LOCATION}"
mkdir -p "${TEST_CASE_LOCATION}"

python3 "${MAPPING_TESTER}"/generate.py      --setup "${TEST_LOCATION}"/config.json --outdir "${TEST_CASE_LOCATION}" --template "${MAPPING_TESTER}"/config-template.xml --exit
python3 "${MAPPING_TESTER}"/preparemeshes.py --setup "${TEST_LOCATION}"/config.json --outdir "${TEST_CASE_LOCATION}"

cd "${TEST_CASE_LOCATION}" && bash ./runall.sh
bash ./postprocessall.sh

cd "${TEST_LOCATION}"

python3 "${MAPPING_TESTER}"/gatherstats.py --outdir "${TEST_CASE_LOCATION}" --file statistics.csv