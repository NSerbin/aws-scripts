import argparse
import boto3
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

def delete_objects(s3_bucket, profile, expression, s3_suffix=""):
    # Create a session using the specified profile
    session = boto3.Session(profile_name=profile)

    # Create an S3 client using the session
    s3_client = session.client("s3")

    # Compile the regular expression pattern
    pattern = re.compile(f"{expression}$")

    # List objects and filter using the regular expression
    objects_to_delete = []

    paginator = s3_client.get_paginator("list_objects_v2")
    pages = paginator.paginate(Bucket=s3_bucket, Prefix=s3_suffix)
    
    for page in pages:
        contents = page.get("Contents", [])
        keys = [obj["Key"] for obj in contents if pattern.search(obj["Key"])]
        objects_to_delete.extend(keys)

    # Delete objects in parallel using ThreadPoolExecutor
    batch_size = 1000
    with ThreadPoolExecutor() as executor:
        futures = []
        for i in range(0, len(objects_to_delete), batch_size):
            batch = objects_to_delete[i:i + batch_size]
            future = executor.submit(s3_client.delete_objects, Bucket=s3_bucket, Delete={"Objects": [{"Key": key} for key in batch]})
            futures.append(future)

        # Wait for all deletion tasks to complete
        for future in as_completed(futures):
            response = future.result()
            deleted_keys = [obj["Key"] for obj in response.get("Deleted", [])]
            print(f"Deleted files: {deleted_keys}")

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
