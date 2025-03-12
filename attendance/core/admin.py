from django.contrib import admin

from .models import Attendance, Course, Session

# Register your models here.
admin.site.register(Attendance)
admin.site.register(Session)
admin.site.register(Course)
