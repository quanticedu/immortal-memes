# Copyright 2022 Quantic School of Business and technology
#
# This Flask application emulates part of the functionality of an
# AWS API Gateway using Elastic Beanstalk. It was written because
# the AWS Learner Lab does not allow for the use of API Gateway.
#
# The following functionality from the API Gateway is emulated. If
# a capability isn't specifically mentioned (e.g. a $default stage),
# assume it's not implemented:
#
#    API types: HTTP
#    Integrations: Lambda
#    Methods: any (including the ANY method specifier)
#    Path variables: yes, except for greedy variables.
#    CORS: Access-Control-Allow-Origin only
#
# For more information on Flask, see 
# https://flask.palletsprojects.com/en/2.1.x/. A few notes:
#
#    - To initialize a Flask web server, you add routes that the
#      server will respond to using add_url_rule(). Part of each
#      URL rule is a view function that gets called when the 
#      URL path matches the rule.
#    - When the server processes a request, Flask sets a global
#      variable named request with the details of the request.
#
# This application uses the boto3 library to invoke AWS Lambda
# functions. You can learn more about boto3 here:
# https://boto3.amazonaws.com/v1/documentation/api/latest/index.html

from flask import Flask, request
from flask_cors import CORS
import json, boto3
from botocore.config import Config

class LambdaInvoker():
    """Represents a callable invoker for an AWS Lambda function.

    Normally you pass add_url_rule a view_func. However, we needed to
    have a way to associate the view_func with a particular AWS
    Lambda function. So we actually make a callable object that
    has as attributes the Lambda function and path.
    
    Attributes:
        region: A string with the region containing the Lambda to invoke.
                Note that this feature is untested for cases in which the
                Lambda is in a different region than the Elastic Beanstalk
                instance running the API Gateway emulator.
        function: A string with the name of the Lambda to invoke.
        path: A string with the URL path for this route.
    """
    def __init__(self, region, function, path):
        self.region = region
        self.function = function
        self.path = path

    def __call__(self, **path_params):
        """Invokes the Lambda.
        
        Invokes the Lambda function and returns the response. This is called
        by Flask based on URL rules added to the application with
        add_url_rule().
        
        Args:
            path_params: A dictionary with the parameters in the path (e.g. if
                         the route was specified as /foo/{bar} and the path is
                         /foo/42, the dictionary will be {"bar": 42}).

        Returns:
            The response from the Lambda function, or an error message.
        """

        # build the payload the lambda function expects to see. see
        # https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-develop-integrations-lambda.html
        # for details on the payload that an API Gateway sends a Lambda.
        # we omit requestContext (TODO see about including later) and 
        # stageVariables (didn't appear in an actual payload sent to 
        # Lambda from API Gateway). 
        payload = {
            "version": "2.0",
            "routeKey": f"{request.method} {self.path}",
            "rawPath": request.path,
            "rawQueryString": str(request.query_string),
            "cookies": [
                f"{cookie[0]}={cookie[1]}" for cookie in request.cookies.items()
            ],
            "headers": dict(request.headers),
            "queryStringParameters": dict(request.args),
            "body": request.get_data(as_text=True),
            "isBase64Encoded": False
        }

        if (path_params):
            payload["pathParameters"] = path_params

        # invoke the Lambda function. We don't need to specify credentials
        # if we give the Elastic Beanstalk instance a role
        invoke_config = Config(
            region_name=self.region
        )
        client = boto3.client("lambda", config=invoke_config)
        lambda_response = client.invoke(
            FunctionName=self.function,
            InvocationType="RequestResponse",
            Payload=json.dumps(payload)
        )

        # now send the response. note that flask_cors does not include
        # CORS headers on responses without bodies.
        return lambda_response["Payload"].read(), lambda_response["StatusCode"]

        # code to test the gateway and client locally follows
        #if self.function == "im-get-thumbnails":
        #    tns = []
        #    for i in range(5):
        #        tns.append({
        #            "id": i,
        #            "userName": "John",
        #            "timePosted": 1654197470000,
        #            "timeToLive": 20 + i,
        #            "imageUrl": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAoAAAAKCAIAAAACUFjqAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAACYSURBVChTYwACDg6O+fPn/4eBX/sPvrd0eCujAkQgaYgKiNyPVWvfaRlB5BDSQBAlr/hY1wQuAURfsgoYCgoKgHLOHFz3pJSQ5b5W1gINY/j+/ftUdy9kucue/v9+/IDYxfB90TK4BBD1Cooiu5QB2SFAOYg74CoY4HJAA9vb2yHSQABRAZWGOAQI0FSApOFyEABXkZGRAQBG/IfkyHRaggAAAABJRU5ErkJggg=="
        #        })

        #    return {"statusCode": 200, "body": tns}, 200
        #elif self.function == "im-post-meme":
        #    return {"statusCode": 200}, 200
        #elif self.function == "im-health-check":
        #    return {"statusCode": 200, "body": "healthy"}, 200
        #elif self.function == "im-get-meme":
        #    print("returning")
        #    return {
        #        "statusCode": 200,
        #        "body": {
        #            "id": 1,
        #            "imageUrl": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAoAAAAKCAIAAAACUFjqAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAACYSURBVChTYwACDg6O+fPn/4eBX/sPvrd0eCujAkQgaYgKiNyPVWvfaRlB5BDSQBAlr/hY1wQuAURfsgoYCgoKgHLOHFz3pJSQ5b5W1gINY/j+/ftUdy9kucue/v9+/IDYxfB90TK4BBD1Cooiu5QB2SFAOYg74CoY4HJAA9vb2yHSQABRAZWGOAQI0FSApOFyEABXkZGRAQBG/IfkyHRaggAAAABJRU5ErkJggg==",
        #            "userName": "John",
        #            "timePosted": 1654197470000,
        #            "timeToLive": 30,
        #            "likes" : ["Pete", "Fred"]
        #        }
        #    }, 200
        #elif self.function == "im-put-like":
        #    return {"statusCode": 200}, 200
        #else:
        #    return {"statusCode": 500, "error": f"bad function {self.function}"}, 500

# convenience function to raise an exception if a required dictionary
# entry is missing
def get_required_entry(dictionary, key, exception_text):
    """Raises an exception if a required dictionary key is missing.
    
    Args:
        dictionary: The dictionary.
        key: The key.
        exception_text: The text of the exception.
        
    Returns:
        The value for the given key.
        
    Raises:
        Exception: the key wasn't found.
    """
    result = dictionary.get(key)

    if not result:
        raise Exception(exception_text)

    return result

# Start building the app. Elastic Beanstalk looks for a callable named 
# application.
application = Flask(__name__)

# load the config file
config = None

try:
    with open("apis.json") as config_file:
        apis = json.load(config_file)
except Exception as err:
    err_str = f"Config file error: {err}"
    application.add_url_rule(
        "/",
        endpoint="config_err",
        view_func=lambda: err_str
    )
    apis = []

# build the route handlers
cors_origins = []

try:
    for api in apis:
        api_name = get_required_entry(
            api,
            "api_name",
            "API missing required api_name"
        )
        api_type = get_required_entry(
            api,
            "api_type",
            f"API {api_name} missing required type"
        )

        if api_type == "HTTP":
            routes = get_required_entry(
                api,
                "routes",
                f"API {api_name} missing required routes"
            )
            integrations = get_required_entry(
                api,
                "integrations",
                f"API {api_name} missing required integrations"
            )
 
            for route in routes:
                method = get_required_entry(
                    route,
                    "method",
                    f"Route in API {api_name} missing required method"
                )

                if method == "ANY":
                    method = None

                path = get_required_entry(
                    route,
                    "path",
                    f"Route in API {api_name} missing required path"
                )

                integration_target = get_required_entry(
                    route,
                    "integration_target",
                    f"Route in API {api_name} missing required integration_target"
                )

                for integration in integrations:
                    integration_type = get_required_entry(
                        integration,
                        "type",
                        f"integration in API {api_name} missing required type"
                    )

                    if integration_type == "lambda":
                        integration_function = get_required_entry(
                            integration,
                            "function",
                            f"lambda integration in API {api_name} missing required function"
                        )

                        if integration_function == integration_target:
                            region = get_required_entry(
                                integration,
                                "region",
                                f"lambda integraion in API {api_name} missing required region"
                            )

                            endpoint_name = f"{method if method else 'no method'} {path} {region} {integration_function}"
                            # See https://flask.palletsprojects.com/en/2.1.x/api/#flask.Flask.add_url_rule
                            # for documentation on the add_url_rule() method.
                            # In the first argument, Flask uses <> for path 
                            # variable delimiters, so we replace API Gateway's
                            # curly braces. The endpoint argument provides a
                            # unique name for the URL rule.
                            application.add_url_rule(
                                # Flask uses <> for path variable delimiters
                                path.replace("{", "<").replace("}", ">"),
                                endpoint=endpoint_name,
                                methods=[method] if method else None,
                                view_func=LambdaInvoker(region, integration_function, path)
                            )

                            print(f"Added endpoint named '{endpoint_name}'")

                            break # from: for integration in integrations
                    else: # from: if integration_type == "lambda"
                        raise Exception(f"integration type {integration_type} not implemented")

                else: # from: for integration in integrations
                    raise Exception(f"route in API {api_name} has no corresponding integration target")

        else: # from: if api_type == "HTTP"
            raise Exception(f"api type {api_type} not implemented")

        cors_origins += api.get("Access-Control-Allow-Origin", [])

except Exception as err:
    # reset the application and add an error route
    print(f"Gateway config error: {err}. Setting default / route.")
    application = Flask(__name__)
    err_str = f"Gateway config error: {err}"
    application.add_url_rule(
        "/", 
        endpoint="config_err", 
        view_func=lambda: err_str
    )

if cors_origins:
    CORS(application, origins=cors_origins)

# run the app.
if __name__ == "__main__":
    application.run()
