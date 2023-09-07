import os
import json
import traceback
import bcrypt
import boto3

dynamodb = boto3.resource("dynamodb")

# Get table name and second Lambda function name from environment variables
TABLE_NAME = os.environ.get("USER_TABLE_NAME")
LAMBDA_FUNCTION_NAME = os.environ.get("LAMBDA_FUNCTION_NAME")

def handler(event, context):
    try:
        # Retrieve user data from the request body
        user_data = json.loads(event["body"])
        username = user_data["username"]
        password = user_data["password"]
        name = user_data["name"]

        # Perform data validation
        if not username or not password or not name:
            return {"statusCode": 400, "body": json.dumps({"error": "Missing required fields"})}

        # Check if the user already exists in the DynamoDB table
        table = dynamodb.Table(TABLE_NAME)
        response = table.get_item(Key={"username": username})
        if "Item" in response:
            return {"statusCode": 409, "body": json.dumps({"error": "User already exists"})}

        # Hash the password
        hashed_password = hash_password(password)

        # Call the second Lambda to generate the Data Encryption Key (DEK) and CMK
        response = boto3.client("lambda").invoke(
            FunctionName=LAMBDA_FUNCTION_NAME,
            InvocationType="RequestResponse",
            Payload=json.dumps({"username": username}),
        )
        response_payload = json.loads(response["Payload"].read().decode("utf-8"))

        # Check if the "encrypted_data_encryption_key" key exists in the response_payload dictionary
        if "encrypted_data_encryption_key" not in response_payload:
            return {
                "statusCode": 500,
                "body": json.dumps({"error": "CMK alias not found in the response. {}".format(str(response_payload))}),
            }

        encrypted_data_encryption_key = response_payload["encrypted_data_encryption_key"]

        # Store user data, encrypted DEK, and CMK ARN in DynamoDB
        item = {
            "username": username,
            "name": name,
            "password": hashed_password.decode("utf-8"),
            "Encrypted_DEK": encrypted_data_encryption_key,
        }
        table.put_item(Item=item)

        return {
            "statusCode": 200,
            "body": json.dumps({"message": "User registration successful"}),
        }
    except KeyError as e:
        error_message = "Missing required field: {}".format(str(e))
        traceback.print_exc()
        return {"statusCode": 400, "body": json.dumps({"error": error_message})}
    except Exception as e:
        error_message = "Internal server error: {}".format(str(e))
        traceback.print_exc()
        return {"statusCode": 500, "body": json.dumps({"error": error_message})}


def hash_password(password):
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    return hashed_password
