import json
import base64
import io
import time
from PIL import Image
import boto3
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    ### get the meme id from path parameters
    meme_id = event["pathParameters"]["id"]

    ### get entry from the database
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table("im-memes")
    db_meme = table.get_item(Key={"id": meme_id})

    ### return an error code if the meme's not in the database
    meme = db_meme.get("Item")

    if not meme:
        return {
            "statusCode": 404,
            "body": json.dumps("no such meme")
        }

    # create an in-memory file
    with io.BytesIO() as in_mem_file:
        ### download the image data into the in-memory 
        ### file. return error code if it doesn't exist
        s3 = boto3.resource("s3")
        bucket = s3.Bucket("<username>-quantic-im-memes")
        
        try:
            bucket.download_fileobj(f"/memes/{meme_id}", in_mem_file)
        except ClientError as error:
            if error.response["Error"]["Code"] == "404":
                return {
                    "statusCode": 404,
                    "body": json.dumps("no such meme")
                }
            else:
                raise error

        # load the meme as an image to get its type
        image = Image.open(in_mem_file)

        time_now = int(time.time())

        ### build the object to return
        return_data = {
            "imageUrl": (f"data:image/{image.format};base64,"
                         + base64.b64encode(in_mem_file.getvalue()).decode("utf-8")),
            "id": meme_id,
            "userName": meme["userName"],
            "timePosted": int(meme["timePosted"]),
            "timeToLive": int(meme["timeToDie"]) - time_now,
            "likes": meme.get("likes", [])
        }

    return {
        "statusCode": 200,
        "body": json.dumps(return_data)
    }