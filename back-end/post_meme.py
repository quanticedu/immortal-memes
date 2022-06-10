import json
import uuid
import time
import base64
import io
from PIL import Image

# need to import one more library here

def lambda_handler(event, context):
    # get the meme data from the event body
    meme_data = 

    # the data URL format is "data:image/<format>;base64,<data>" so we split
    # the data from the header, then the extension from the header
    header, data = meme_data["image"].split(";base64,")
    extension = header.split("image/")[-1]

    if extension not in ("bmp", "gif", "jpeg", "png", "tiff"):
        # return a status code 400 error

    # use Pillow (https://pillow.readthedocs.io/en/stable/index.html)
    # to load the image and save it and its thumbnail in S3. the file's
    # name will be its ID, which we generate as a random UUID
    id = uuid.uuid4().hex

    # base 64 conversion code courtesy of https://stackoverflow.com/a/68989496/4062628
    # save PIL image to S3 courtesy of https://stackoverflow.com/a/56241877/4062628 
    
    # get the PIL image from the base64 data, then save it in an in-memory
    # file-like object
    image = Image.open(io.BytesIO(base64.decodebytes(bytes(data, "utf-8"))))
    in_mem_file = io.BytesIO()
    image.save(in_mem_file, format=image.format)
    in_mem_file.seek(0)
    
    # now write it to the S3 bucket
    s3 = 
    bucket = 
    bucket.
    
    # make a thumbnail and repeat the process above
    image.thumbnail((200, 200))
    in_mem_file = io.BytesIO()
    
    # JPG doesn't support an alpha channel, so we need to remove it
    # if it exists. conversion courtesy of 
    # https://stackoverflow.com/a/49255449/4062628
    if image.mode in ("RGBA", "P"):
        image = image.convert("RGB")
    
    image.save(in_mem_file, format="jpeg")
    in_mem_file.seek(0)
    bucket.

    # write the entry to the database
    posted = int(time.time()) # current epoch time in seconds
    timeToDie = posted + 24 * 60 * 60
    db_entry = {
        "id": id,
        "userName": meme_data["userName"],
        "timePosted": posted,
        "timeToDie": timeToDie
    }
    
    dynamodb = 
    table = 
    table.

    # return success code and id of the meme

