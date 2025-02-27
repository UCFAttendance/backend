import json
import logging
import os
import re
import time
from typing import Any, Dict

import boto3
from botocore.exceptions import ClientError
from django.core.management.base import BaseCommand

from attendance.core.models import Attendance

LOGGER = logging.getLogger(__name__)


class FaceRecognitionProcessor:
    def __init__(self):
        self.sqs = boto3.client("sqs")
        self.s3 = boto3.client("s3")
        self.rekognition = boto3.client("rekognition")
        self.queue_url = os.environ.get("SQS_QUEUE_URL")

    def process_message(self, message: Dict[str, Any]) -> None:
        try:
            s3_event = json.loads(message["Body"])

            if "Event" in s3_event and s3_event["Event"] == "s3:TestEvent":
                return

            for s3_rec in s3_event["Records"]:
                bucket_name: str = s3_rec["s3"]["bucket"]["name"]
                object_key: str = s3_rec["s3"]["object"]["key"]
                LOGGER.info(f"Processing S3 Record: {bucket_name}/{object_key}")

                # Validate object key format
                REGEX = r"^\d+/\d+_(init|\d+)\.jpeg$"
                if not re.match(REGEX, object_key):
                    LOGGER.warning(f"Invalid object key format: {object_key}")
                    return

                # Parse the object key
                parts = object_key.split("/")
                student_id = parts[0]
                attendance_parts = parts[1].split("_")
                attendance_id = attendance_parts[0]
                init_or_timestamp = attendance_parts[1].split(".")[0]

                if init_or_timestamp == "init":
                    self.handle_init_image(bucket_name, object_key, student_id, attendance_id)
                else:
                    self.handle_attendance_image(bucket_name, object_key, student_id, attendance_id)

        except Exception as e:
            LOGGER.error(f"Error processing message: {e}")
            raise

    def handle_init_image(self, bucket_name: str, object_key: str, student_id: str, attendance_id: str) -> None:
        LOGGER.info(f"Copying init image to {student_id}/init.jpeg")

        try:
            self.s3.copy_object(
                Bucket=bucket_name, CopySource=f"{bucket_name}/{object_key}", Key=f"{student_id}/init.jpeg"
            )
            self.update_attendance_record(attendance_id, Attendance.FaceRecognitionStatus.SUCCESS)
        except ClientError as e:
            LOGGER.error(f"Failed to copy init image: {e}")
            raise

    def handle_attendance_image(self, bucket_name: str, object_key: str, student_id: str, attendance_id: str) -> None:
        LOGGER.info(f"Comparing face with {student_id}/init.jpeg")
        face_compare_result = Attendance.FaceRecognitionStatus.FAILED
        if self.compare_face(bucket_name, f"{student_id}/init.jpeg", object_key):
            face_compare_result = Attendance.FaceRecognitionStatus.SUCCESS

        LOGGER.info(f"Face compare result: {face_compare_result}")
        self.update_attendance_record(attendance_id, face_compare_result)

    def compare_face(self, bucket_name: str, init_image: str, target_image: str) -> bool:
        try:
            response = self.rekognition.compare_faces(
                SourceImage={
                    "S3Object": {
                        "Bucket": bucket_name,
                        "Name": init_image,
                    }
                },
                TargetImage={
                    "S3Object": {
                        "Bucket": bucket_name,
                        "Name": target_image,
                    }
                },
            )
            return len(response["FaceMatches"]) > 0

        except self.rekognition.exceptions.InvalidParameterException:
            return False

    def update_attendance_record(self, attendance_id: str, face_recognition_status: str) -> None:
        try:
            Attendance.objects.filter(id=attendance_id).update(
                face_recognition_status=face_recognition_status,
                ís_present=True if face_recognition_status == Attendance.FaceRecognitionStatus.SUCCESS else False,
            )
            LOGGER.info(
                f"Successfully updated attendance record - id: {attendance_id}, " f"status: {face_recognition_status}"
            )

        except Exception as e:
            LOGGER.error(f"Failed to update attendance record: {e}")
            raise

    def run(self):
        while True:
            try:
                response = self.sqs.receive_message(
                    QueueUrl=self.queue_url, MaxNumberOfMessages=10, WaitTimeSeconds=20
                )

                if "Messages" in response:
                    for message in response["Messages"]:
                        try:
                            self.process_message(message)
                            # Delete message after successful processing
                            self.sqs.delete_message(QueueUrl=self.queue_url, ReceiptHandle=message["ReceiptHandle"])
                        except Exception as e:
                            LOGGER.error(f"Failed to process message: {e}")
                            # Don't delete message on failure - it will return to queue
                            continue
            except Exception as e:
                LOGGER.error(f"Error in main processing loop: {e}")
                time.sleep(5)  # Prevent tight loop on persistent errors


class Command(BaseCommand):
    help = "Process messages from SQS"

    def handle(self, *args, **options):
        processor = FaceRecognitionProcessor()
        processor.run()
