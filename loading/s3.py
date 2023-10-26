import boto3
from config import CONFIG
import time

def init_s3_client():
    print("Initializing S3 client...")
    client = boto3.client(
        's3',
        endpoint_url=CONFIG.AWS_ENDPOINT_URL,
        aws_access_key_id=CONFIG.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=CONFIG.AWS_SECRET_ACCESS_KEY
    )
    return client

def upload_file(client, bucket, location, data):
    start_time = time.time()
    print("Uploading file...")
    client.put_object(
        Bucket=bucket,
        Key=location,
        Body=data
    )
    print(f"Took {time.time() - start_time} seconds to upload file {location} to S3.")
