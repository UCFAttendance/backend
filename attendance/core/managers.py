from django.db import models, transaction
from django.core.files.base import ContentFile
import base64
import logging

LOGGER = logging.getLogger(__name__)

class AttendanceManager(models.Manager):
    def save_face_recognition_result(self, attendance_id: str, face_recognition_status: str, face_image: str) -> None:
        try:
            with transaction.atomic():
                attendance = self.get(id=attendance_id)

                if face_recognition_status == 'SUCCESS':
                    attendance.face_recognition_status = self.model.FaceRecognitionStatus.SUCCESS
                    attendance.is_present = True
                else:
                    attendance.face_recognition_status = self.model.FaceRecognitionStatus.FAILED

                if face_image:
                    try:
                        image_data = base64.b64decode(face_image)
                        file_name = f"face_{attendance_id}"
                        attendance.face_image.save(
                            file_name,
                            ContentFile(image_data),
                            save=False
                        )
                    except Exception as img_error:
                        LOGGER.error(f"Failed to process face image: {img_error}")

                attendance.save()

            LOGGER.info(
                f"Successfully updated attendance record - id: {attendance_id}, "
                f"status: {face_recognition_status}"
            )

        except self.model.DoesNotExist:
            LOGGER.error(f"Attendance record not found: {attendance_id}")
            raise
        except Exception as e:
            LOGGER.error(f"Failed to update attendance record: {e}")
            raise
