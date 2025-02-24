import hashlib

from django.core.cache import cache
from django.db import models
from attendance.core.managers import AttendanceManager

class Course(models.Model):
    name = models.CharField(max_length=50)
    teacher_id = models.ForeignKey("users.User", on_delete=models.CASCADE)

    class Meta:
        unique_together = ("name", "teacher_id")

    def __str__(self):
        return f"{self.name} - {self.teacher_id}"


class Session(models.Model):
    course_id = models.ForeignKey(Course, on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(blank=True, null=True)
    salt = models.CharField(max_length=32, editable=False)
    face_recognition_enabled = models.BooleanField(default=False)
    location_enabled = models.BooleanField(default=False)
    longitude = models.FloatField(blank=True, null=True, default=None)
    latitude = models.FloatField(blank=True, null=True, default=None)

    def __str__(self):
        return f"{self.course_id} - {self.start_time} - {self.end_time}"

    def generate_secret(self) -> str:
        # Generate secret from session data
        data = f"{self.course_id}-{self.id}-{self.start_time}-{self.salt}"
        secret = hashlib.sha256((data).encode("utf-8")).hexdigest()

        # Store secret in cache
        cache.set(
            f"teacher:{self.course_id.teacher_id.id}:session:{self.id}",
            {
                "secret": secret,
                "face_recognition_enabled": self.face_recognition_enabled,
                "location_enabled": self.location_enabled,
                "longitude": self.longitude,
                "latitude": self.latitude,
            },
            timeout=60 * 60 * 3,
        )
        return secret


def get_face_image_path(instance: "Attendance", filename: str):
    return f"{instance.student_id.id}/{filename}.jpeg"


class Attendance(models.Model):
    session_id = models.ForeignKey(Session, on_delete=models.CASCADE)
    student_id = models.ForeignKey("users.User", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    longitude = models.FloatField(blank=True, null=True, default=None)
    latitude = models.FloatField(blank=True, null=True, default=None)
    is_present = models.BooleanField(default=False)

    class FaceRecognitionStatus(models.TextChoices):
        NOT_REQUIRED = "NOT_REQUIRED"
        PENDING = "PENDING"
        SUCCESS = "SUCCESS"
        FAILED = "FAILED"

    face_recognition_status = models.CharField(
        max_length=12,
        choices=FaceRecognitionStatus.choices,
        default=FaceRecognitionStatus.NOT_REQUIRED,
    )
    face_image = models.ImageField(upload_to=get_face_image_path, null=True)

    object = AttendanceManager()

    class Meta:
        unique_together = ("session_id", "student_id")

    def __str__(self):
        return f"{self.session_id} - {self.student_id} - {self.created_at} - {self.is_present}"
