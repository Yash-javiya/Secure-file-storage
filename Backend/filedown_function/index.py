import os
import json
import base64
import boto3
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

def get_secret():
    # Utility function to retrieve the S3 master key from AWS Secrets Manager
    secret_name = os.environ.get("S3_MASTER_KEY_SECRET_NAME")
    if not secret_name:
        raise Exception("S3_MASTER_KEY_SECRET_NAME environment variable not set.")
    
    region_name = "us-east-1"

    session = boto3.session.Session()
    client = session.client(service_name="secretsmanager", region_name=region_name)

    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        raise e

    # Decrypts secret using the associated KMS key.
    secret = get_secret_value_response["SecretString"]
    # Ensure the key is of the correct length (e.g., AES-256 key length)
    s3_master_key = secret.encode("utf-8")[:32]  # Use first 32 bytes for AES-256
    return s3_master_key

# Get the S3 master key
SECRET_KEY = get_secret()

def decrypt_file_content(encrypted_text):
    # Extract the IV from the encrypted text (first AES.block_size bytes)
    iv = encrypted_text[: AES.block_size]

    # Create the cipher object with AES mode and CBC (Cipher Block Chaining) padding
    cipher = AES.new(SECRET_KEY, AES.MODE_CBC, iv)

    try:
        # Decrypt the ciphertext and remove padding
        decrypted_text = unpad(
            cipher.decrypt(encrypted_text[AES.block_size :]), AES.block_size
        )
        return decrypted_text
    except Exception as e:
        print("Decryption error:", e)
        raise e

def handler(event, context):
    # Handles file download from S3 with decryption
    body = json.loads(event["body"])
    username = body["username"]
    file_name = body["file_name"]

    # Retrieve the encrypted file from S3
    s3_bucket_name = os.environ.get("S3_BUCKET_NAME")
    if not s3_bucket_name:
        return {
            "statusCode": 500,
            "body": json.dumps({"message": "S3_BUCKET_NAME environment variable not set."}),
            "headers": {
                "Content-Type": "application/json"  # Set the response content type to JSON
            },
        }
    
    s3_key = f"{username}/{file_name}"
    s3_client = boto3.client("s3")

    try:
        response = s3_client.get_object(Bucket=s3_bucket_name, Key=s3_key)
        encrypted_data = response["Body"].read()
        # Return the status in the response
        response = {
            "statusCode": 200,
            "body": encrypted_data,
            "headers": {"Content-Type": "application/json"},
        }

    except Exception as e:
        message = f"Error downloading file: {str(e)}"
        status_code = 500
        response = {
            "statusCode": status_code,
            "body": json.dumps({"message": message}),
            "headers": {"Content-Type": "application/json"},
        }
        return response

    try:
        # Base64 decode the encrypted data before decryption
        encrypted_data_decoded = base64.b64decode(encrypted_data)

        # Decrypt the file content
        decrypted_file_content = decrypt_file_content(encrypted_data_decoded)

        message = "File decrypted and downloaded successfully."
        status_code = 200
    except Exception as e:
        message = f"Error: {str(e)}"
        status_code = 500

    return response
