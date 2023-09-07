import os
import json
import hashlib
import re
import boto3
import base64
import secrets

# Get table name and lab role name from environment variables
TABLE_NAME = os.environ.get("USER_TABLE_NAME")
LAB_ROLE_NAME = os.environ.get("LAB_ROLE_NAME")

dynamodb = boto3.resource("dynamodb")
kms = boto3.client("kms")

def handler(event, context):
    try:
        username = event["username"]
        encrypted_dek, cmk_alias = get_or_generate_encrypted_dek(username)
        
        return {
            "encrypted_data_encryption_key": encrypted_dek,
            "key_alias": cmk_alias,
        }
    except Exception as e:
        error_message = f"Error generating CMK alias or checking DEK existence: {str(e)}"
        raise Exception(error_message) from e

def clean_username_and_derive_cmk_alias(username):
    clean_username = re.sub(r"[^a-zA-Z0-9]", "", username)
    salt = hashlib.sha256(username.encode()).hexdigest()
    salted_username = clean_username + salt
    cmk_alias = hashlib.sha256(salted_username.encode()).hexdigest()
    return clean_username, cmk_alias

def get_encrypted_dek(username):
    table = dynamodb.Table(TABLE_NAME)
    response = table.get_item(Key={"username": username})
    item = response.get("Item")
    encrypted_dek = item["Encrypted_DEK"] if item and "Encrypted_DEK" in item else None
    return encrypted_dek

def generate_data_encryption_key():
    data_encryption_key = secrets.token_bytes(32)
    return data_encryption_key

def encrypt_data_encryption_key(data_encryption_key, key_id):
    response = kms.encrypt(KeyId=key_id, Plaintext=data_encryption_key)
    ciphertext_blob_base64 = base64.b64encode(response["CiphertextBlob"]).decode("utf-8")
    return ciphertext_blob_base64

def get_kms_key_arn_from_alias(alias_name):
    try:
        alias_response = kms.describe_key(KeyId=alias_name)
        kms_key_arn = alias_response["KeyMetadata"]["Arn"]
        return kms_key_arn
    except kms.exceptions.NotFoundException:
        create_response = kms.create_key()
        key_id = create_response["KeyMetadata"]["KeyId"]
        update_key_policy(key_id)

        try:
            kms.create_alias(AliasName=alias_name, TargetKeyId=key_id)
        except kms.exceptions.AlreadyExistsException:
            existing_alias_response = kms.list_aliases(KeyId=key_id)
            kms_key_arn = existing_alias_response["Aliases"][0]["AliasArn"]
            return kms_key_arn
        return get_kms_key_arn_from_alias(alias_name)
    except Exception as e:
        raise Exception(f"Error occurred while fetching the KMS Key ARN: {str(e)}")

def update_key_policy(key_id):
    lab_role_arn = get_role_arn(LAB_ROLE_NAME)
    key_policy = {
        "Version": "2012-10-17",
        "Id": "key-default-1",
        "Statement": [
            {
                "Sid": "Enable IAM User Permissions",
                "Effect": "Allow",
                "Principal": {"AWS": ["arn:aws:iam::407226150316:root", lab_role_arn]},
                "Action": "kms:*",
                "Resource": "*",
            }
        ],
    }
    key_policy_json = json.dumps(key_policy)
    kms.put_key_policy(KeyId=key_id, PolicyName="default", Policy=key_policy_json)

def get_role_arn(role_name):
    iam = boto3.client("iam")
    response = iam.get_role(RoleName=role_name)
    return response["Role"]["Arn"]

def get_or_generate_encrypted_dek(username):
    table = dynamodb.Table(TABLE_NAME)
    response = table.get_item(Key={"username": username})
    item = response.get("Item")

    if item and "Encrypted_DEK" in item and "CMKAlias" in item:
        encrypted_dek = item["Encrypted_DEK"]
        cmk_alias = item["CMKAlias"]
    else:
        data_encryption_key = generate_data_encryption_key()
        clean_username, cmk_alias = clean_username_and_derive_cmk_alias(username)
        cmk_arn = get_kms_key_arn_from_alias(f"alias/{cmk_alias}")
        encrypted_dek = encrypt_data_encryption_key(data_encryption_key, cmk_arn)

    return encrypted_dek, cmk_alias
