#!/bin/bash

SOURCE_BUCKET=$1
DESTINATION_BUCKET=$2
FILE_LIST=$4
PROFILE=$3
SUCCESS_OUTPUT_FILE="success.txt"
SUCCESS_OUTPUT_FILE="error.txt"
# Iterate over each file in the list
while IFS= read -r file
do
  echo "Copying $file..."

  # Use AWS CLI to copy the file from the source to destination bucket
  aws s3 cp --profile "${PROFILE}" "s3://$SOURCE_BUCKET/$file" "s3://$DESTINATION_BUCKET/$file"

  # Check if the copy command succeeded
  if [ $? -eq 0 ]; then
    echo "Success: $file copied." >> "$SUCCESS_OUTPUT_FILE"
  else
    echo "Error: Failed to copy $file." >> "$ERROR_OUTPUT_FILE"
  fi  

done < "$FILE_LIST"
