#!/bin/bash

PROFILE="$1"
SOURCE_BUCKET="$2"
DESTINATION_BUCKET="$3"

# List all ".mp4" files in the source S3 bucket
files=$(aws s3 ls "s3://$SOURCE_BUCKET" --profile "${PROFILE}" --recursive | awk '{if ($4 ~ /\.mp4$/) print $4}')

# Iterate over the files
for file in $files; do
  echo "Processing file: $file"

  # Restore the file from Glacier (if it's archived)
  restore_status=$(aws s3api --profile "${PROFILE}" head-object --bucket "$SOURCE_BUCKET" --key "$file" | jq -r '.Restore')
  
  if [[ "$restore_status" == "null" ]]; then
    echo "File is not archived in Glacier. Skipping..."
    continue
  fi
  
  if [[ "$restore_status" != "ongoing-request=\"false\", expiry-date="* ]]; then
    echo "Restoring file from Glacier..."
    aws s3api --profile "${PROFILE}" restore-object --bucket "$SOURCE_BUCKET" --key "$file" --restore-request '{"Days": 7}'
    echo "File restoration initiated. Please wait for it to complete before continuing."
    continue
  fi

  # Copy the file to the destination S3 bucket
  echo "Copying file to destination bucket..."
  aws s3 --profile "${PROFILE}" cp "s3://$SOURCE_BUCKET/$file" "s3://$DESTINATION_BUCKET/$file"
  
  echo "File copied successfully."
done
