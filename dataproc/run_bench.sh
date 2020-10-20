#!/bin/bash
set -e

DFSIO_JAR=file:///usr/lib/hadoop-mapreduce/hadoop-mapreduce-client-jobclient-3.2.1-tests.jar
DFSIO_PROPS="test.build.data=gs://${BUCKET_ID}/,fs.default.name=gs://${BUCKET_ID}/"
NUM_FILES=1
FILE_SIZE=1000MB
RESULT_PATH=/tmp/dataproc_result.txt

function run_job() {
    gcloud \
        --project ${PROJECT_ID} \
        dataproc jobs submit hadoop \
        --cluster ${CLUSTER_ID} \
        --jar ${DFSIO_JAR} \
        --properties="${DFSIO_PROPS},${DFSIO_PROPS_EXTRA}" \
        --region $REGION_ID \
        -- \
        TestDFSIO -read -nrFiles ${NUM_FILES} -fileSize ${FILE_SIZE} -resFile /tmp/test_dsfio.log \
        -warmupCount $1 -repeatCount $2 2> /tmp/dataproc_output.txt
    echo "Run $1 $2 $DFSIO_PROPS_EXTRA" >> ${RESULT_PATH}
    cat /tmp/dataproc_output.txt | grep Throughput >> ${RESULT_PATH}
}

for i in {1..10}
do 
    DFSIO_PROPS_EXTRA="fs.gs.grpc.enable=false"
    run_job 0 1
    DFSIO_PROPS_EXTRA="fs.gs.grpc.enable=true"
    run_job 0 1

    DFSIO_PROPS_EXTRA="fs.gs.grpc.enable=false"
    run_job 0 10
    DFSIO_PROPS_EXTRA="fs.gs.grpc.enable=true"
    run_job 0 10
    DFSIO_PROPS_EXTRA="fs.gs.grpc.enable=false"
    run_job 10 10
    DFSIO_PROPS_EXTRA="fs.gs.grpc.enable=true"
    run_job 10 10

    DFSIO_PROPS_EXTRA="fs.gs.grpc.enable=false"
    run_job 0 50
    DFSIO_PROPS_EXTRA="fs.gs.grpc.enable=true"
    run_job 0 50
    DFSIO_PROPS_EXTRA="fs.gs.grpc.enable=false"
    run_job 10 50
    DFSIO_PROPS_EXTRA="fs.gs.grpc.enable=true"
    run_job 10 50    
done
