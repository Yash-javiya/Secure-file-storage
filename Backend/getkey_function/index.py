import json
import boto3
import base64
import os
from botocore.exceptions import ClientError
import hashlib
import traceback

lambda_client = boto3.client("lambda")
kms_client = boto3.client("kms")

# Get Lambda function name and KMS key alias prefix from environment variables
LAMBDA_FUNCTION_NAME = os.environ.get("LAMBDA_FUNCTION_NAME")


def handler(event, context):
    username = event.get("queryStringParameters", {}).get("username")

    if not username:
        return {
            "statusCode": 400,
            "body": json.dumps(
                {"message": "Username not provided in the URL parameter."}
            ),
        }

    try:
        # Call the second Lambda to generate the Data Encryption Key (DEK) and CMK
        response = lambda_client.invoke(
            FunctionName=LAMBDA_FUNCTION_NAME,
            InvocationType="RequestResponse",
            Payload=json.dumps({"username": username}),
        )
        response_payload = json.loads(response["Payload"].read().decode("utf-8"))

        # Check if the "encrypted_data_encryption_key" and "key_alias" keys exist in the response_payload dictionary
        if (
            "encrypted_data_encryption_key" not in response_payload
            or "key_alias" not in response_payload
        ):
            raise Exception(
                "Encrypted Data Encryption Key or Key Alias not found in the response. {}".format(
                    str(response_payload)
                )
            )

        encrypted_data_encryption_key = response_payload[
            "encrypted_data_encryption_key"
        ]
        key_alias = response_payload["key_alias"]

        # Decrypt the data encryption key using the CMK
        decrypted_data_encryption_key = decrypt_data_encryption_key(
            encrypted_data_encryption_key, f"alias/{key_alias}", username
        )

        return {
            "statusCode": 200,
            "body": json.dumps(
                {
                    "DataEncryptionKey": base64.b64encode(
                        decrypted_data_encryption_key
                    ).decode("utf-8"),
                    "EncryptedDataEncryptionKey": encrypted_data_encryption_key,
                }
            ),
        }

    except Exception as e:
        error_message = "Error occurred while processing the request: {}".format(str(e))
        raise Exception(error_message) from e


def get_secret():
    # Utility function to retrieve the S3 master key from AWS Secrets Manager
    secret_name = "s3-master-key"
    region_name = "us-east-1"

    session = boto3.session.Session()
    client = session.client(service_name="secretsmanager", region_name=region_name)

    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        raise e

    # Decrypts secret using the associated KMS key.
    secret = get_secret_value_response["SecretString"]
    # Ensure the key is of the correct length (e.g., AES-256 key length
    return secret


def decrypt_data_encryption_key(encrypted_data_encryption_key, key_alias, username):
    # Decode the base64 encoded encrypted DEK
    ciphertext_blob = base64.b64decode(encrypted_data_encryption_key)

    # Decrypt the DEK using the CMK alias
    response = kms_client.decrypt(CiphertextBlob=ciphertext_blob, KeyId=key_alias)

    try:
        # Encode the get_secret() response and the username to bytes
        secret_bytes = get_secret().encode("utf-8")
        username_bytes = username.encode("utf-8")

        # Concatenate the encoded get_secret() response with the encoded username
        secret_with_username = secret_bytes + username_bytes

        # The decrypted DEK is in Plaintext, which is the data encryption key
        decrypted_data_encryption_key = hashlib.sha256(secret_with_username).digest()

        return decrypted_data_encryption_key

    except Exception as e:
        traceback.print_exc()  # Print the stack trace
        raise e
