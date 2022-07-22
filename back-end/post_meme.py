import json
import uuid
import time
import base64, binascii
import io
from PIL import Image, UnidentifiedImageError
### need to import one more library here

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
        pass ### return a status code 400 error and the string "badly-formed image data"

    if extension not in ("bmp", "gif", "jpeg", "png", "tiff"):
        pass ### return a status code 400 error and the string "can't work with {extension} images"

    # use Pillow (https://pillow.readthedocs.io/en/stable/index.html)
    # to load the image (base 64 conversion code courtesy of
    # https://stackoverflow.com/a/68989496/4062628)
    
    # get the PIL image from the base64 data
    try:
        image = Image.open(io.BytesIO(base64.decodebytes(bytes(data, "utf-8"))))
    except (UnidentifiedImageError, binascii.Error):
        pass ### return a status code 400 and the string "badly-formed image data"

    # use a random UUID as the id for the meme (both the full image
    # and thumbnail)
    id = uuid.uuid4().hex

    # get the S3 bucket
    s3 = ### get the service resource
    bucket = ### get the sub-resource

    # save it in an in-memory file-like object
    with io.BytesIO() as in_mem_file:
        image.save(in_mem_file, format=image.format)
        in_mem_file.seek(0)
    
        # upload from the in-memory object to S3
        bucket. ### apply the method to upload a file object to the /memes folder
    
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
        bucket. ### upload to the /thumbnails folder using the same id as the meme

    # write the entry to the database
    posted = int(time.time()) # current epoch time in seconds
    timeToDie = posted + 24 * 60 * 60
    db_entry = {
        "id": id,
        "userName": meme_data["userName"],
        "timePosted": posted,
        "timeToDie": timeToDie
    }
    
    dynamodb = ### get the service resource
    table = ### get the sub-resource
    table. ### apply the method to add an item to the table

    ### return success code and id of the meme

