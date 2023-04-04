import json
import uuid
import time
import base64, binascii
import io
from PIL import Image, UnidentifiedImageError
import boto3

def lambda_handler(event, context):
    # event is a JSON string as described in https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-develop-integrations-lambda.html
    # the client provides data as a dictionary in the "body" entry as follows:
    # { "image": <string, base 64 data URL>,
    #   "userName": <string, user's name> }

    meme_data = json.loads(event["body"])

    # the data URL format is "data:image/<format>;base64,<data>" so we split
    # the data from the header, then the extension from the header
    try:
        header, data = meme_data["image"].split(";base64,")
        extension = header.split("image/")[-1]
    except ValueError:
        return {
            "statusCode": 400,
            "body": json.dumps("badly-formed image data")
        }

    if extension not in ("bmp", "gif", "jpeg", "png", "tiff"):
        return {
            "statusCode": 400,
            "body": json.dumps("badly-formed image data")
        }

    # use Pillow (https://pillow.readthedocs.io/en/stable/index.html)
    # to load the image (base 64 conversion code courtesy of
    # https://stackoverflow.com/a/68989496/4062628)
    
    # get the PIL image from the base64 data
    try:
        image = Image.open(io.BytesIO(base64.decodebytes(bytes(data, "utf-8"))))
    except (UnidentifiedImageError, binascii.Error):
        return {
            "statusCode": 400,
            "body": json.dumps("badly-formed image data")
        }

    # use a random UUID as the id for the meme (both the full image
    # and thumbnail)
    id = uuid.uuid4().hex

    # get the S3 bucket
    s3 = boto3.resource("s3")
    bucket = s3.Bucket("<username>-quantic-im-memes")

    # save it in an in-memory file-like object
    # if you're unfamiliar with the "with" statement, read this: https://www.geeksforgeeks.org/with-statement-in-python/
    with io.BytesIO() as in_mem_file:
        image.save(in_mem_file, format=image.format)
        in_mem_file.seek(0)
        bucket.upload_fileobj(in_mem_file, f"/memes/{id}")
    
    # make a thumbnail and repeat the process above
    image.thumbnail((200, 200))
    
    # JPG doesn't support an alpha channel, so we need to remove it
    # if it exists. conversion courtesy of 
    # https://stackoverflow.com/a/49255449/4062628
    if image.mode in ("RGBA", "P"):
        image = image.convert("RGB")
    
    with io.BytesIO() as in_mem_file:
        image.save(in_mem_file, format="jpeg")
        in_mem_file.seek(0)
        bucket.upload_fileobj(in_mem_file, f"/thumbnails/{id}")

    # write the entry to the database
    posted = int(time.time()) # current epoch time in seconds
    timeToDie = posted + 24 * 60 * 60
    db_entry = {
        "id": id,
        "userName": meme_data["userName"],
        "timePosted": posted,
        "timeToDie": timeToDie
    }
    
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table("im-memes")
    table.put_item(Item=db_entry)

    return {
        "statusCode": 200,
        "body": json.dumps({ "id": id })
    }

