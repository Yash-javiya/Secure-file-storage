import boto3
import jwt
from botocore.exceptions import ClientError
import os


def get_jwt_secret():
    secret_name = os.getenv("JWT_SECRET_NAME")
    if not secret_name:
        raise Exception("JWT_SECRET_NAME environment variable not set.")
    region_name = "us-east-1"

    session = boto3.session.Session()
    client = session.client(service_name="secretsmanager", region_name=region_name)

    try:
        response = client.get_secret_value(SecretId=secret_name)
        secret = response["SecretString"]
        return secret
    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code")
        if error_code == "ResourceNotFoundException":
            raise Exception("JWT secret not found. Please configure it properly.")
        else:
            raise Exception("Failed to retrieve JWT secret.")


def fetch_user_details(username):
    table_name = os.getenv("USER_TABLE_NAME")
    if not table_name:
        raise Exception("USER_TABLE_NAME environment variable not set.")
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(table_name)

    try:
        # Fetch the user details based on the provided username (email)
        response = table.get_item(Key={"username": username})
        user_details = response.get("Item")
        return user_details
    except ClientError as e:
        # Handle any errors while fetching user details
        raise Exception("Error fetching user details")


def handler(event, context):
    response = {"isAuthorized": False, "context": None}

    try:
        if "headers" in event and "authorization" in event["headers"]:
            authorization_header = event["headers"]["authorization"]
            token = authorization_header.split("Bearer ")[-1].strip()

            try:
                jwt_secret = get_jwt_secret()

                # Verify and decode the JWT token
                payload = jwt.decode(token, jwt_secret, algorithms=["HS256"])
                username = payload["username"]

                # Fetch user details from the database
                user_details = fetch_user_details(username)

                if user_details:
                    # Additional validation can be performed here if needed

                    # Return true indicating the request is authorized
                    response["isAuthorized"] = True
                    response["context"] = {
                        "userId": username,
                        # Add additional context if needed
                    }
                else:
                    # Handle case when the user does not exist or is not valid
                    response["message"] = "Invalid user"
            except jwt.ExpiredSignatureError:
                # Handle expired token
                response["message"] = "Expired token"
            except jwt.InvalidTokenError as e:
                # Handle invalid token with a specific error message
                response["message"] = f"Invalid token: {str(e)}"
            except Exception as e:
                # Handle other errors
                response["message"] = str(e)

    except Exception as e:
        # Handle exceptions during authorization process
        response["message"] = str(e)

    return response
