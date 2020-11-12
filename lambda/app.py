""" An AWS Lambda function demonstrating features like:
 - responding to HTTP GET requests .. e.g. serving an HTML page
 - responding to HTTP POST requests ..  e.g returning mp3 or wav
 - storing data in a dynamo db
 - calling AWS services like polly
 - calling another AWS lambda function
 - calling a native library or executable
"""
import json
import logging
from os import chmod
from shutil import copyfile

from dynamo import RequestDB
from polly import synthesize

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

copyfile("./ffmpeg", '/tmp/ffmpeg')
chmod("/tmp/ffmpeg", 755)

RequestDB.init("dynamodb")
SCOPE = "awscd"


def lambda_handler(event, context) -> dict:
    """
    :param event: input data, usually a dict, but can also be list, str, int, float, or NoneType type.
    :param context: object providing information about invocation, function, and execution environment
    :return: dict with http header, status code, and body
    """
    if not event.get('httpMethod'):  # invoked directly e.g. to keep it warm
        return {"status_code": 400, "message": "Bad Request"}

    status_code, content_type, content = get(event['path']) if 'GET' == event['httpMethod'] else post(event)
    return {
        "statusCode": status_code,
        "headers": {
            # Cross-Origin Resource Sharing (CORS) allows a server to indicate any other origins than its own,
            # from which a browser should permit loading of resources.
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': True,
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET',
            'Content-Type': content_type,
        },
        "body": content
    }


def get(file_path: str) -> (int, str, str):
    """ :returns: HTTP code, content-type, content of the requested text file. API Gateway is blocking all but /ui/* """
    logging.info(file_path)

    if file_path.endswith('.css'):
        content_type = 'text/css; charset=UTF-8'
    elif file_path.endswith('.js'):
        content_type = 'text/javascript; charset=UTF-8'
    else:
        content_type = 'text/html; charset=UTF-8'
    try:
        with open('.' + file_path, 'r') as file:
            content = file.read()
    except OSError:
        return 404, 'text/html; charset=UTF-8', file_path + " not found"
    return 200, content_type, content


def post(event: dict) -> (int, str, str):
    """ :returns HTTP code, content-type, and message """
    params = json.loads(event['body'])  # if event.get('body') else event
    if params:
        function = event['path'].split('/')[-1].lower()
        if function == 'synthesize':
            RequestDB.create(SCOPE, event['requestContext']['identity']['sourceIp'], params['text'])
            content_type = "audio/wav" if params['format'] == 'wav' else 'audio/mpeg'
            content = synthesize(params['text'], params['translate'], params['format'])
            return 200, content_type, json.dumps({"b64": content})
    return 400, 'application/json; charset=UTF-8', 'Bad Request'
