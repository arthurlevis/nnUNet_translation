#!/bin/bash

# Source directories
TRAIN_A="./brain-sample-paired/train/A"
TRAIN_B="./brain-sample-paired/train/B"
VAL_A="./brain-sample-paired/val/A"
VAL_B="./brain-sample-paired/val/B"
TEST_A="./brain-sample-paired/test/A"
TEST_B="./brain-sample-paired/test/B"

# Target directories
NNUNET_RAW="./raw/Dataset001_MRCT"
IMAGES_TR="${NNUNET_RAW}/imagesTr"
LABELS_TR="${NNUNET_RAW}/labelsTr"
IMAGES_TS="${NNUNET_RAW}/imagesTs"
LABELS_TS="${NNUNET_RAW}/labelsTs"

# # Create all directories
# mkdir -p "${IMAGES_TR}" "${LABELS_TR}" "${IMAGES_TS}" "${LABELS_TS}"

# Function to process training/validation pairs
process_pairs() {
    local src_a=$1
    local src_b=$2
    
    for mr_path in "${src_a}"/*.nii.gz; do
        base=$(basename "${mr_path}")
        ct_name="${base/real_A_/}"
        ct_path="${src_b}/real_B_${ct_name}"
        
        cp "${mr_path}" "${IMAGES_TR}/${ct_name}"
        cp "${ct_path}" "${LABELS_TR}/${ct_name}"
    done
}

# Function to process test pairs
process_test_pairs() {
    local src_a=$1
    local src_b=$2
    
    for mr_path in "${src_a}"/*.nii.gz; do
        base=$(basename "${mr_path}")
        ct_name="${base/real_A_/}"
        ct_path="${src_b}/real_B_${ct_name}"
        
        cp "${mr_path}" "${IMAGES_TS}/${ct_name}"
        cp "${ct_path}" "${LABELS_TS}/${ct_name}"
    done
}

# Process all data
process_pairs "${TRAIN_A}" "${TRAIN_B}"
process_pairs "${VAL_A}" "${VAL_B}"
process_test_pairs "${TEST_A}" "${TEST_B}"
