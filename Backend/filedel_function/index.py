import os
import boto3
import json

def handler(event, context):
    try:
        # Handles file removal from S3
        body = json.loads(event["body"])
        username = body["username"]
        filename = body["filename"]

        # Get the S3 bucket name from the environment variable
        bucket_name = os.environ.get("S3_BUCKET_NAME")
        if not bucket_name:
            return {
                "statusCode": 500,
                "body": json.dumps({"message": "S3_BUCKET_NAME environment variable not set."}),
                "headers": {
                    "Content-Type": "application/json"  # Set the response content type to JSON
                },
            }

        # Replace 'your_folder_path/' with the specific folder path (prefix)
        folder_path = f"{username}/"

        # Construct the full S3 object key for the file to be removed
        object_key = f"{folder_path}{filename}"

        s3_client = boto3.client("s3")

        # Delete the specified object (file) from the S3 bucket
        s3_client.delete_object(Bucket=bucket_name, Key=object_key)

        return {
            "statusCode": 200,
            "body": json.dumps({"message": f"File {filename} removed successfully."}),
            "headers": {
                "Content-Type": "application/json"  # Set the response content type to JSON
            },
        }
    except KeyError as ke:
        # Handle missing keys in the body
        error_message = f"KeyError: {ke}"
        return {"statusCode": 400, "body": error_message}
    except Exception as e:
        # Log any other unexpected exception
        error_message = f"An error occurred: {str(e)}"
        return {"statusCode": 500, "body": error_message}
