import json
import boto3
import time

def lambda_handler(event, context):
    ### get the meme_id and user_name
    
    ### query the database for the meme's info. return 404 error if it's not in the database.

    ### return 400 error if the meme was already liked by this user or if this user posted the meme
        
    ### build an update expression to add the like and increment timeToDie by one hour

    ### update the item

    ### return 201 success
