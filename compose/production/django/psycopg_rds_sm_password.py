import sys
import time

import psycopg
import boto3

suggest_unrecoverable_after = 30
start = time.time()

# Get the secret from AWS Secrets Manager
client = boto3.client("secretsmanager", region_name="${AWS_REGION}")
response = client.get_secret_value(SecretId="${ATTENDANCE_SECRET_ID}")
secret = response["SecretString"]

while True:
    try:
        psycopg.connect(
            dbname="${POSTGRES_DB}",
            user="${POSTGRES_USER}",
            password=secret,
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
