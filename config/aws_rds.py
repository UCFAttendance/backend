import os
import json

import boto3
from django.db.backends.postgresql import base


class DatabaseWrapper(base.DatabaseWrapper):
    def get_connection_params(self):
        params = super().get_connection_params()
        client = boto3.client("secretsmanager", region_name=os.environ["AWS_REGION"])
        response = client.get_secret_value(SecretId=os.environ["ATTENDANCE_SECRET_ID"])
        secret = json.loads(response["SecretString"])
        params["password"] = secret["password"]

        return params
