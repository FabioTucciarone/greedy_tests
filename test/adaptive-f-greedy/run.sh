TEST_NAME="adaptive-f-greedy"
ROOT_LOCATION="$(pwd)"
RUN_LOCATION="${ROOT_LOCATION}/test/${TEST_NAME}"
TEST_LOCATION="${ROOT_LOCATION}/test/${TEST_NAME}/testcase"
ASTE_LOCATION="${ROOT_LOCATION}/../aste"

rm -rf "${TEST_LOCATION}"
mkdir -p "${TEST_LOCATION}"

cd $RUN_LOCATION
python3 generate.py $RUN_LOCATION/config.yaml $RUN_LOCATION $ASTE_LOCATION
chmod +x $TEST_LOCATION/run.sh

cd $ROOT_LOCATION
bash $TEST_LOCATION/run.sh