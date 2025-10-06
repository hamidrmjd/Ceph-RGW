import subprocess
import os
from typing import Union, List
from concurrent.futures import ThreadPoolExecutor, as_completed


# First with s3cmd --configure, enter the correct acc_key, sec_key and endpoint. then run this app

def create_buckets(bucketName: str, bucketCount: int) -> List[str]:
    """
    Create multiple S3 buckets using s3cmd.

    Args:
        bucketName (str): The base name of the bucket.
        bucketCount (int): Number of buckets to create.

    Returns:
        List[str]: List of created (or existing) bucket names.
    """
    bucket_list = []
    for i in range(bucketCount):
        bucket = f"{bucketName}{i}"

        # Check if bucket exists
        check_cmd = ["s3cmd", "ls", f"s3://{bucket}"]
        result = subprocess.run(check_cmd, capture_output=True, text=True)

        if result.returncode == 0 and bucket in result.stdout:
            print(f"Bucket {bucket} already exist!!!!!!")
        else:
            # Create bucket
            create_cmd = ["s3cmd", "mb", f"s3://{bucket}"]
            result = subprocess.run(create_cmd, capture_output=True, text=True)

            if result.returncode == 0:
                print(f"Bucket {bucket} created successfully.")
            else:
                print(f"Failed to create bucket {bucket}. Error: {result.stderr}")

        bucket_list.append(bucket)

    return bucket_list


def put_objects(
    buckets: Union[str, List[str]],
    filePath: str,
    capacityTarget: str,
    cleanup: bool = False,
    max_workers: int = 10
):
    """
    Upload objects into one or more S3 buckets until the target capacity is reached.
    Uploads run in parallel for stress testing.

    Args:
        buckets (str | List[str]): Target bucket(s).
        filePath (str): Path to the file to upload.
        capacityTarget (str): Target capacity (e.g., "100GB", "50MB").
        cleanup (bool): Whether to remove objects after uploading.
        max_workers (int): Number of parallel upload threads.
    """
    # Convert human-readable capacity target into bytes
    def parse_size(size_str):
        size_str = size_str.upper()
        if size_str.endswith("GB"):
            return int(size_str[:-2]) * 1024**3
        elif size_str.endswith("MB"):
            return int(size_str[:-2]) * 1024**2
        elif size_str.endswith("KB"):
            return int(size_str[:-2]) * 1024
        else:
            return int(size_str)  # assume bytes

    # Normalize buckets input
    if isinstance(buckets, str):
        buckets = [buckets]

    # Check file size
    file_size = os.path.getsize(filePath)
    target_size = parse_size(capacityTarget)

    if file_size == 0:
        print("File size is zero! Cannot upload.")
        return

    # Calculate number of uploads needed
    upload_count = target_size // file_size
    if upload_count == 0:
        print("Target capacity is smaller than file size. Uploading once.")
        upload_count = 1

    print(f"File size: {file_size} bytes")
    print(f"Target capacity: {target_size} bytes")
    print(f"Total uploads required: {upload_count}")
    print(f"Distributing uploads across {len(buckets)} bucket(s) with {max_workers} parallel workers...")

    def upload_task(index: int, bucket: str):
        object_name = f"{os.path.basename(filePath)}_{index}"
        put_cmd = ["s3cmd", "put", filePath, f"s3://{bucket}/{object_name}"]
        result = subprocess.run(put_cmd, capture_output=True, text=True)
        if result.returncode == 0:
            return f"[{bucket}] Uploaded object {object_name}"
        else:
            return f"[{bucket}] Failed to upload {object_name}. Error: {result.stderr}"

    # Run uploads in parallel
    futures = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for i in range(upload_count):
            bucket = buckets[i % len(buckets)]  # round-robin distribution
            futures.append(executor.submit(upload_task, i, bucket))

        for future in as_completed(futures):
            print(future.result())

    # Cleanup if required
    if cleanup:
        for bucket in buckets:
            print(f"Cleaning up bucket {bucket}...")
            cleanup_cmd = ["s3cmd", "rm", f"s3://{bucket}", "--recursive", "--force"]
            result = subprocess.run(cleanup_cmd, capture_output=True, text=True)

            if result.returncode == 0:
                print(f"Bucket {bucket} cleaned up successfully.")
            else:
                print(f"Failed to cleanup bucket {bucket}. Error: {result.stderr}")


if __name__ == "__main__":
    # Example: create 5 buckets named "test-bucket-0" .. "test-bucket-4"
    buckets = create_buckets("node1-bucket-", 5)

    # Example: upload 100GB worth of objects across all created buckets in parallel
    put_objects(
        buckets=buckets,
        filePath="/root/windows",    # File path to upload
        capacityTarget="5000GB",
        cleanup=False,
        max_workers=20  # number of parallel uploads
    )
