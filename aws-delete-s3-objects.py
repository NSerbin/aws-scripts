import argparse
import boto3
import re
from concurrent.futures import ThreadPoolExecutor

def delete_objects(s3_bucket, profile, expression, s3_suffix=""):
    # Create a session using the specified profile
    session = boto3.Session(profile_name=profile)

    # Create an S3 client using the session
    s3_client = session.client("s3")

    # Create a paginator for listing objects
    paginator = s3_client.get_paginator("list_objects_v2")

    # Create a thread pool executor
    executor = ThreadPoolExecutor()

    # Function to delete a single object
    def delete_object(key):
        print(f"Deleting file: {key}")
        s3_client.delete_object(Bucket=s3_bucket, Key=key)

    # Compile the regular expression pattern
    pattern = re.compile(f"{expression}$")

    # Loop through the pages and filter objects
    pages = paginator.paginate(Bucket=s3_bucket, Prefix=s3_suffix)
    for page in pages:
        contents = page.get("Contents", [])
        keys = [obj["Key"] for obj in contents if pattern.search(obj["Key"])]
        for key in keys:
            executor.submit(delete_object, key)

    # Shutdown the executor and wait for all tasks to complete
    executor.shutdown(wait=True)

    print("All files deleted successfully.")

def main():
    parser = argparse.ArgumentParser(description="Delete files from an S3 bucket based on a regular expression")
    parser.add_argument("--S3_BUCKET", required=True, help="The name of your S3 bucket (ONLY THE PREFIX)")
    parser.add_argument("--PROFILE", required=True, help="The AWS profile to use (located in .aws/credentials)")
    parser.add_argument("--EXPRESSION", required=True, help="The regular expression to be used for filtering files")
    parser.add_argument("--S3_SUFFIX", default="", help="Suffix to append to the S3 path")

    args = parser.parse_args()

    delete_objects(args.S3_BUCKET, args.PROFILE, args.EXPRESSION, args.S3_SUFFIX)


if __name__ == "__main__":
    main()
