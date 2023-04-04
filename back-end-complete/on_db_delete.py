import json
import boto3

def lambda_handler(event, context):
    objects = []
    
    for item in event["Records"]:
        meme_id = item["dynamodb"]["Keys"]["id"]["S"]
        objects.append({"Key": f"/memes/{meme_id}"})
        objects.append({"Key": f"/thumbnails/{meme_id}"})
        
    s3 = boto3.resource("s3")
    bucket = s3.Bucket("jriehl-quantic-im-memes")
    bucket.delete_objects(Delete={"Objects": objects})
    return