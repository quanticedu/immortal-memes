import json
import boto3
import time

def lambda_handler(event, context):
    ### get the meme_id and user_name
    meme_id = event["pathParameters"]["id"]
    event_body = json.loads(event["body"])
    user_name = event_body["userName"]
    
    ### query the database for the meme's info. return 404 error if it's not in the database.
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

    ### return 400 error if the meme was already liked by this user or if this user posted the meme
    likes = meme.get("likes", [])

    if (user_name in likes
            or user_name == meme["userName"]):
        return {
            "statusCode": 400,
            "body": json.dumps("You can't like this!")
        }
    
    ### build an update expression to add the like and increment timeToDie by one hour
    likes.append(user_name)
    expression_attribute_values = {
        ":hour": 60 * 60,
        ":new_likes": likes
    }
    update_expression = (
        "SET timeToDie = timeToDie + :hour, "
        "likes = :new_likes"
    )

    ### update the item
    table.update_item(
        Key={"id": meme_id},
        UpdateExpression=update_expression,
        ExpressionAttributeValues=expression_attribute_values)

    ### return 201 success
    return {
        "statusCode": 201,
        "body": json.dumps(f"/{meme_id}")
    }