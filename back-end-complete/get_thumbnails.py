import json
import boto3
import base64
import io
import time
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    ### get the S3 service resource
    s3 = boto3.resource("s3")
    bucket = s3.Bucket("<username>-quantic-im-memes")
    
    ### get all meme entries from the database
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table("im-memes")
    db_memes = table.scan()
    memes = db_memes["Items"]

    # build the response for each entry. id, userName, and timePosted
    # simply pass through. we compute timeToLive from timeToDie and
    # generate the data URL using PIL and base64
    time_now = int(time.time())
    thumbnails = []
    
    for meme in memes:
        # skip this thumbnail if it's past its time to die
        if time_now > int(meme["timeToDie"]):
            continue

        # create a thumbnail item with metadata and image data
        thumbnail = {
            "timeToLive": int(meme["timeToDie"]) - time_now,
            "timePosted": int(meme["timePosted"]),
            "userName": meme["userName"],
            "id": meme["id"]
        }

        # load the image into an in-memory file object
        with io.BytesIO() as in_mem_file:
            try:
                bucket.download_fileobj(f"/thumbnails/{meme['id']}", in_mem_file)
            except ClientError as error:
                if error.response["Error"]["Code"] == "404":
                    continue
                else:
                    raise error
        
            # now write the image into the thumbnail as a base64 data URL
            # base 64 conversion code courtesy of https://stackoverflow.com/a/68989496/4062628
            thumbnail["imageUrl"] = (
                "data:image/jpeg;base64," 
                + base64.b64encode(in_mem_file.getvalue()).decode("utf-8"))

        # add the thumbnail to the response
        thumbnails.append(thumbnail)
        
    return {
        "statusCode": 200,
        "body": json.dumps(thumbnails)
    }
