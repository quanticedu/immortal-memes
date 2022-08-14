import json
import base64
import io
import time
from PIL import Image
### include missing imports here

def lambda_handler(event, context):
    ### get the meme id from path parameters
    meme_id = 

    ### get entry from the database

    ### return an error code if the meme's not in the database

    # create an in-memory file
    with io.BytesIO() as in_mem_file:
        ### download the image data into the in-memory 
        ### file. return error code if it doesn't exist

        # load the meme as an image to get its type
        image = Image.open(in_mem_file)

        time_now = int(time.time())

        ### build the object to return
        return_data = {
            "imageUrl": (f"data:image/{image.format};base64,"
                         + base64.b64encode(in_mem_file.getvalue()).decode("utf-8")),
        }

    ### return success code and return_data
