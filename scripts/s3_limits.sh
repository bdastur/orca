#!/bin/bash

################################################################################
# Test S3 Bucket limits. 
################################################################################


if [[ ! -e ~/.aws/s3_limits_data.sh ]]; then
    echo "No test data provided. Exit"
    exit
fi

source ~/.aws/s3_limits_data.sh


function create_bucket {
    echo "Create Bucket:   [${TEST_BUCKET}]"
    cmdout=$(aws s3api create-bucket --bucket ${TEST_BUCKET}) 
    if [[ $? -ne 0 ]]; then
        echo "Bucket creation failed. $cmdout"
        exit 1
    fi  
}

function test_s3_toplevel_folder_count {
    # Params:
    # TOPLEVEL_DIR_COUNT
    # TEST_BUCKET
    # UPLOAD_FILE_PATH
    # First Create the test bucket.

    filepath=$1
    if [[ ! -z $filepath ]]; then
        echo "filepath: $filepath"
        UPLOAD_FILE_PATH=$filepath
    fi
    create_bucket

    sleep 1
    # Create multiple Directories.
    DIRNAME_PREFIX="dir"

    for cnt in `seq 1 $TOPLEVEL_DIR_COUNT`;
    do
        DESTNAME="${DIRNAME_PREFIX}-${cnt}/testobj"
        aws s3api put-object --bucket ${TEST_BUCKET} --key ${DESTNAME} --body ${UPLOAD_FILE_PATH}
        echo "Creating object: [${DESTNAME}]"
    done

    objcount=$(aws s3api list-objects --bucket ${TEST_BUCKET} | grep CONTENTS | wc -l)
    if [[ $objcount -ne $TOPLEVEL_DIR_COUNT ]]; then
        echo "TEST: TOP-LEVEL DIRCOUNT: Failed expected ${TOPLEVEL_DIR_COUNT}, found $objcount"
    else
        echo "TEST: TOP-LEVEL DIRCOUNT: Passed. Buckets created $objcount"
    fi

    # Delete the objects.
    for cnt in `seq 1 $TOPLEVEL_DIR_COUNT`;
    do
        DESTNAME="${DIRNAME_PREFIX}-${cnt}/testobj"
        aws s3api delete-object --bucket ${TEST_BUCKET} --key ${DESTNAME}
        echo "Deleting object: [${DESTNAME}]"
    done

    sleep 10
    echo "Deleting Bucket ${TEST_BUCKET}"
    aws s3api delete-bucket --bucket ${TEST_BUCKET}
}

function test_s3_folder_hierarchy {
    # Params:
    # FOLDER_HIERARCHY.
    # TEST_BUCKET
    # UPLOAD_FILE_PATH

    create_bucket
    sleep 1

    DIRNAME_PREFIX="dir"
    DESTNAME="DIR-1"
    for cnt in `seq  1 ${FOLDER_HIERARCHY}`;
    do
        DESTNAME="${DESTNAME}/SUBDIR"
    done
    echo "DESTNAME: $DESTNAME"

    for cnt in `seq 1 ${TOPLEVEL_DIR_COUNT}`;
    do
        NESTED_DESTNAME="${DESTNAME}/dir-${cnt}/testobj"
        aws s3api put-object --bucket ${TEST_BUCKET} --key ${NESTED_DESTNAME} --body ${UPLOAD_FILE_PATH}
        echo "destname: $NESTED_DESTNAME"
    done

    objcount=$(aws s3api list-objects --bucket ${TEST_BUCKET} | grep CONTENTS | wc -l)
    if [[ $objcount -ne $TOPLEVEL_DIR_COUNT ]]; then
        echo "TEST: TOP-LEVEL DIRCOUNT: Failed expected ${TOPLEVEL_DIR_COUNT}, found $objcount"
    else
        echo "TEST: TOP-LEVEL DIRCOUNT: Passed. Buckets created $objcount"
    fi

    sleep 4

    # Delete the objects.
    for cnt in `seq 1 $TOPLEVEL_DIR_COUNT`;
    do
        NESTED_DESTNAME="${DESTNAME}/dir-${cnt}/testobj"
        aws s3api delete-object --bucket ${TEST_BUCKET} --key ${NESTED_DESTNAME}
        echo "Deleting object: [${NESTED_DESTNAME}]"
    done
    sleep 4

    echo "Deleting Bucket ${TEST_BUCKET}"
    aws s3api delete-bucket --bucket ${TEST_BUCKET}
}


test_s3_toplevel_folder_count
test_s3_folder_hierarchy
test_s3_toplevel_folder_count $UPLOAD_LARGEFILE_PATH


