import json
import sys
import time
import os

import boto3
import psycopg

suggest_unrecoverable_after = 30
start = time.time()

# Get the secret from AWS Secrets Manager
client = boto3.client("secretsmanager", region_name=os.environ["AWS_REGION"])
response = client.get_secret_value(SecretId=os.environ["DB_SECRET_ARN"])
secret = json.loads(response["SecretString"])

username = secret["username"]
password = secret["password"]
host = os.environ["POSTGRES_HOST"]
port = os.environ["POSTGRES_PORT"]
db_name = os.environ["POSTGRES_DB"]

os.environ["DATABASE_URL"] = f"postgres://{username}:{password}@{host}:{port}/{db_name}"
sys.stdout.write("DATABASE_URL has been set.\n")

while True:
    try:
        psycopg.connect(
            dbname="${POSTGRES_DB}",
            user=username,
            password=password,
            host="${POSTGRES_HOST}",
            port="${POSTGRES_PORT}",
        )
        break
    except psycopg.OperationalError as error:
        sys.stderr.write("Waiting for PostgreSQL to become available...\n")

        if time.time() - start > suggest_unrecoverable_after:
            sys.stderr.write(
                "  This is taking longer than expected. The following exception may be indicative of an unrecoverable error: '{}'\n".format(
                    error
                )
            )

    time.sleep(1)
