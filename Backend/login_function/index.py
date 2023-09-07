import os
import json
import bcrypt
import boto3
from jwt import encode
from datetime import datetime, timedelta
from botocore.exceptions import ClientError
import traceback

dynamodb = boto3.resource("dynamodb")

# Get table name and JWT secret name from environment variables
TABLE_NAME = os.environ.get("USER_TABLE_NAME")
JWT_SECRET_NAME = os.environ.get("JWT_SECRET_NAME")

def handler(event, context):
    try:
        # Retrieve user data from the request body
        user_data = json.loads(event["body"])
        username = user_data["username"]
        password = user_data["password"]

        # Retrieve user data from DynamoDB
        user_item = get_user_item(username)

        # Verify the provided password
        verify_password(password, user_item["password"])

        # Generate JWT token
        token = generate_token(username)

        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Login successful", "token": token}),
        }
    except KeyError as e:
        return error_response(400, f"Missing required field: {str(e)}", traceback.format_exc())
    except Exception as e:
        return error_response(401, str(e), traceback.format_exc())


def get_user_item(username):
    table = dynamodb.Table(TABLE_NAME)
    response = table.get_item(Key={"username": username})
    if "Item" not in response:
        raise Exception("User not found")
    return response["Item"]


def verify_password(password, stored_password):
    if not bcrypt.checkpw(password.encode("utf-8"), stored_password.encode("utf-8")):
        raise Exception("Invalid password")


def generate_token(username):
    secret = get_jwt_secret()
    expiration_time = datetime.utcnow() + timedelta(hours=2)
    payload = {"username": username, "exp": expiration_time}
    token = encode(payload, secret, algorithm="HS256")
    return token


def get_jwt_secret():
    region_name = "us-east-1"

    session = boto3.session.Session()
    client = session.client(service_name="secretsmanager", region_name=region_name)

    try:
        response = client.get_secret_value(SecretId=JWT_SECRET_NAME)
        secret = response["SecretString"]
        return secret
    except ClientError as e:
        raise Exception("Failed to retrieve JWT secret")


def error_response(status_code, error_message, stack_trace=None):
    response_body = {"error": error_message}
    if stack_trace:
        response_body["stack_trace"] = stack_trace
    return {"statusCode": status_code, "body": json.dumps(response_body)}
