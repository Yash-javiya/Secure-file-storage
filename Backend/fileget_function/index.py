import os
import boto3
import json
import logging

def handler(event, context):
    try:
        # Handles file download from S3 with decryption
        body = json.loads(event["body"])
        username = body["username"]

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

        s3_client = boto3.client("s3")

        # Get the list of objects in the specified folder of the S3 bucket
        response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=folder_path)

        # Prepare a dictionary to store the file names and contents as form data
        files_data = {}

        # Iterate through the objects in the folder and fetch their content
        for obj in response.get("Contents", []):
            key = obj["Key"]
            obj_data = s3_client.get_object(Bucket=bucket_name, Key=key)
            content = obj_data["Body"].read().decode("utf-8")

            # Store the file name as the key and the content as the value in the form data dictionary
            files_data[key] = content

        return {
            "statusCode": 200,
            "body": json.dumps(files_data),  # Convert the dictionary to a JSON string
            "headers": {
                "Content-Type": "application/json"  # Set the response content type to JSON
            },
        }
    except KeyError as ke:
        # Handle missing keys in the body or response['Contents']
        error_message = f"KeyError: {ke}"
        return {"statusCode": 400, "body": error_message}
    except Exception as e:
        # Log any other unexpected exception
        error_message = f"An error occurred: {str(e)}"
        return {"statusCode": 500, "body": error_message}
