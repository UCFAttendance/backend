import json
import logging
import re
import time
import boto3
import requests
from botocore.exceptions import ClientError
from types import Dict, Any 

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

LOGGER = logging.getLogger(__name__)

class FaceRecognitionProcessor:
    def __init__(self):
        self.sqs = boto3.client('sqs')
        self.s3 = boto3.client('s3')
        self.reckognition = boto3.client('rekognition')
        self.queue_rul = self.get_queue_url()

    def get_queue_url(self) -> str:
        try:
            response = self.sqs.get_queue_url(QueueName='face-recognition-queue')
            return response['QueueUrl']
        except ClientError as e:
            LOGGER.error(f"Failed to get queue URL: {e}")

    def process_message(self, message: Dict[str, Any]) -> None:
        try:
            s3_event = json.loads(message['Body'])

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
            student_id = part[0]
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
                    Bucket=bucket_name,
                    CopySource=f"{bucket_name}/{object_key}",
                    Key=f"{student_id}/init.jpeg",)
            self.send_to_backend(attendance_id, "SUCCESS", object_key)
        except ClientError as e:
            LOGGER.error(f"Failed to copy init image: {e}")
            raise 
    def handle_attendance_image(self, bucket_name: str, object_key: str, student_id: str, attendance_id: str) -> None:  
        LOGGER.info(f"Comparing face with {student_id}/init.jpeg")
        face_compare_result = "SUCCESS" if self.compare_face(
            bucket_name,
            f"{student_id}/init.jpeg",
            object_key
        ) else "FAILED"

        LOGGER.info(f"Face compare result: {face_compare_result}")
        self.send_to_backend(attendance_id, face_compare_result, object_key)

   def compare_face(self, bucket_name: str, init_image: str, target_image: str) -> bool:
       try:
           response := self.reckognition.compare_faces(
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

    def send_to_backend(self, attendance_id: str, face_recognition_status: str, face_image: str) -> None:
        try:
            response = requests.post(
                "http://10.0.15.46:9999/api/v1/image-processing-callback/",
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
                json={
                    "id": attendance_id,
                    "face_recognition_status": face_recognition_status,
                    "face_image": face_image,
                },
                verify=False,
                timeout=5
            )
            response.raise_for_status()
            LOGGER.info(
                f"Backend response - status code: {response.status_code}, body: {response.content}"
            )
        except requests.exceptions.RequestException as e:
            LOGGER.error(f"Failed to send to backend: {e}")
            raise
    
    def run(self):
        
        while True:
            try:
                response = self.sqs.receive_message(
                    QueueUrl=self.queue_url,
                    MaxNumberOfMessages=10,
                    WaitTimeSeconds=20
                )

                if 'Messages' in response:
                    for message in response['Messages']:
                        try:
                            self.process_message(message)
                            # Delete message after successful processing
                            self.sqs.delete_message(
                                QueueUrl=self.queue_url,
                                ReceiptHandle=message['ReceiptHandle']
                            )
                        except Exception as e:
                            LOGGER.error(f"Failed to process message: {e}")
                            # Don't delete message on failure - it will return to queue
                            continue
            except Exception as e:
                LOGGER.error(f"Error in main processing loop: {e}")
                time.sleep(5)  # Prevent tight loop on persistent errors

def main():
    processor = FaceRecognitionProcessor()
    processor.run()

if __name__ == "__main__":
    main()
