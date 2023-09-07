import os
import json
import base64
import boto3
import cgi
from io import BytesIO
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Random import get_random_bytes
from botocore.exceptions import ClientError

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

def encrypt_file_content(plain_text):
    # Generate a random initialization vector (IV)
    iv = get_random_bytes(AES.block_size)

    # Create the cipher object with AES mode and CBC (Cipher Block Chaining) padding
    cipher = AES.new(SECRET_KEY, AES.MODE_CBC, iv)

    # Pad the plaintext to match the block size of the cipher
    padded_plain_text = pad(plain_text, AES.block_size)

    # Perform the encryption
    encrypted_text = cipher.encrypt(padded_plain_text)

    # Return the IV concatenated with the encrypted text
    return base64.b64encode(iv + encrypted_text)

def handler(event, context):
    # Decode the base64-encoded body
    body = base64.b64decode(event["body"])

    # Create a file-like object from the body bytes
    body_file = BytesIO(body)

    # Parse the multipart form data
    environ = {
        "REQUEST_METHOD": "POST",
        "CONTENT_TYPE": event["headers"]["content-type"],
    }
    form = cgi.FieldStorage(fp=body_file, environ=environ)

    # Retrieve the file field
    file_field = form["file"]
    file_name = form["filename"].value  # Retrieve the file name from the form data
    content_type = file_field.type
    file_content = file_field.file.read()
    file_content_bytes = file_content.encode("utf-8")
    
    # Get the username from the request
    username = form["username"].value

    # Encrypt the file content
    encrypted_file_content = encrypt_file_content(file_content_bytes)

    # Upload the encrypted file to S3
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
        s3_client.put_object(
            Bucket=s3_bucket_name, Key=s3_key, Body=file_content
        )
        message = "File uploaded and encrypted successfully."
        status_code = 200
    except Exception as e:
        message = f"Error: {str(e)}"
        status_code = 500

    # Return the status in the response
    response = {
        "statusCode": status_code,
        "body": json.dumps({"message": message, "file_name": file_name}),
        "headers": {"Content-Type": "application/json"},
    }

    return response
