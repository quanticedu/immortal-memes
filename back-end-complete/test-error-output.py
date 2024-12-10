import json
import boto3
from botocore.exceptions import ClientError
import io

def lambda_handler(event, context):
    s3 = boto3.resource("s3")
    bucket = s3.Bucket("<meme bucket>")

    with io.BytesIO() as file:
        try:
            bucket.download_fileobj("foo", file)
        except ClientError as error:
            print(error.response)