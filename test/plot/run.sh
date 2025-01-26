
TEST_NAME="plot"

export ROOT_LOCATION="$(pwd)"
RUN_LOCATION="${ROOT_LOCATION}/test/${TEST_NAME}"
TEST_LOCATION="${ROOT_LOCATION}/test/${TEST_NAME}/testcase"
ASTE_SRC="${ROOT_LOCATION}/../aste/src"
ASTE_BUILD="${ROOT_LOCATION}/../aste/build"
MAPPING_TESTER="${ROOT_LOCATION}/../aste/tools/mapping-tester"

rm -rf "${TEST_LOCATION}"
mkdir -p "${TEST_LOCATION}"

echo ""
echo "[TEST] generate.py"
echo ""

python3 "${MAPPING_TESTER}"/generate.py --setup "${RUN_LOCATION}"/config.json --outdir "${TEST_LOCATION}" --template "${MAPPING_TESTER}"/config-template.xml --exit

echo ""
echo "[TEST] preparemeshes.py"
echo ""

python3 "${MAPPING_TESTER}"/preparemeshes.py --setup "${RUN_LOCATION}"/config.json --outdir "${TEST_LOCATION}"

echo ""
echo "[TEST] runall.sh"
echo ""

cd "${TEST_LOCATION}"
bash ./runall.sh

echo ""
echo "[TEST] preparemeshes.py"
echo ""

bash ./postprocessall.sh

echo ""
echo "[TEST] gatherstats.py"
echo ""

cd "${RUN_LOCATION}"

python3 "${MAPPING_TESTER}"/gatherstats.py --outdir "${TEST_LOCATION}" --file statistics.csv
python3 gather_greedy_stats.py --outdir "${TEST_LOCATION}" --file greedy_values.csv