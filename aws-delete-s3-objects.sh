#!/bin/bash

# Help function
function help {
    echo "Usage: ./script.sh <S3_BUCKET> <PROFILE> <EXPRESSION> [S3_SUFFIX]"
    echo ""
    echo "Arguments:"
    echo "  S3_BUCKET     The name of your S3 bucket (ONLY THE PREFIX)"
    echo "  PROFILE       The AWS profile to use (located in .aws/credentials)"
    echo "  EXPRESSION    The expression to be used for filtering files"
    echo "  S3_SUFFIX     (Optional) Suffix to append to the S3 path"
}

# Check if help option is specified
if [[ "$1" == "--help" ]]; then
    help
    exit 0
fi

# Check if all required arguments are provided
if [[ $# -lt 3 ]]; then
    echo "Error: Insufficient arguments."
    echo ""
    help
    exit 1
fi

# Set your S3 bucket name
S3_BUCKET="$1"

# Set the AWS Profile to use (located in .aws/credentials)
PROFILE="$2"

# Set the expression to be used
EXPRESSION="$3"

S3_SUFFIX="${4:-}"

# Construct the S3 path based on the presence of S3_SUFFIX
if [[ -n $S3_SUFFIX ]]; then
    S3_PATH="s3://${S3_BUCKET}/${S3_SUFFIX}"
else
    S3_PATH="s3://${S3_BUCKET}"
fi

# List all files in the bucket and filter by the expression
files=$(aws s3 ls "$S3_PATH" --profile "$PROFILE" --recursive | awk '{if ($4 ~ /'"$EXPRESSION"'/) print $4}')

# Loop through the files and delete each one
for file in $files
do
    echo "Deleting file: $file"
    aws s3 rm --profile "$PROFILE" "s3://${S3_BUCKET}/${file}"
done

echo "All files deleted successfully.."
