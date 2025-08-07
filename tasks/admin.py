from django.contrib import admin
from .models import Task, Task_Checkup, UserPoints

# Register your models here.
admin.site.register(Task)
admin.site.register(Task_Checkup)
admin.site.register(UserPoints)
