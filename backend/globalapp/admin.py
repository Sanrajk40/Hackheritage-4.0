from django.contrib import admin
from .models import globe_employee
from django.contrib.auth.models import User,Group
# Register your models here.

admin.site.register(globe_employee)
admin.site.unregister(User)
admin.site.unregister(Group)