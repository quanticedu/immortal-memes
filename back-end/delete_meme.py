import json
import boto3

def lambda_handler(event, context):
    # event should be as follows: { "memeId": <string> }
    
    # delete the appropriate DynamoDB records from im-memes and im-likes 
    
    # delete the meme and thumbnail files

    return {
        'statusCode': 200,
        'body': json.dumps("")
    }
