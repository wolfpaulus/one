import logging
import uuid
from binascii import hexlify
from datetime import datetime
from hashlib import sha256, pbkdf2_hmac
from os import urandom

from boto3 import resource
from botocore.exceptions import ClientError


class RequestDB:
    """ Dynamodb actions: create, update, verify, delete, status """
    TABLE_NAME = "lambdaOneRequests"
    dynamodb = None
    table = None

    @classmethod
    def init(cls, res: str):
        """ Setup a local or AWS dynamodb """
        if res == "dynamodb":
            cls.dynamodb = resource("dynamodb")
            cls.table = cls.dynamodb.Table(cls.TABLE_NAME)

    @classmethod
    def _create_key(self):
        """
        Look here, for creating a UUID using Python in Lambda and storing this in elasticache:
        https://stackoverflow.com/questions/35625658/aws-lambda-w-python-uuid-on-dynamo-db-concept
        :return: unique id
        """
        return uuid.uuid4().hex

    @classmethod
    def hash_pin(cls, ip: str) -> str:
        """ Hash an ip for storing, not hashing empty ip """
        if not ip:
            return ip
        salt = sha256(urandom(60)).hexdigest().encode('ascii')
        hashed_pin = pbkdf2_hmac('sha512', ip.encode('utf-8'), salt, 100000)
        hashed_pin = hexlify(hashed_pin)
        return (salt + hashed_pin).decode('ascii')

    @classmethod
    def create(cls, scope: str, ip: str, text: str):
        """
        saves scope and hashed ip in a in table,
        """
        if not scope or not ip or not text:
            return 400, "Bad Request"
        try:
            key = scope + RequestDB._create_key()
            logging.info("Checking if key is new " + str(key))
            response = cls.table.get_item(Key={'key': key, 'scope': scope})
            if "Item" in response:
                return 500, "Unique key creation failed"
            logging.info("Creating record for " + str(key))
            response = cls.table.put_item(
                Item={'key': key,
                      'scope': scope,
                      'ip': cls.hash_pin(ip),
                      'created': datetime.utcnow().isoformat(),
                      'text': text})
            logging.info(str(response))
            return 200, "Record Created"
        except ClientError as e:
            logging.error(str(e))
            return 500, e.response['Error']['Message']
