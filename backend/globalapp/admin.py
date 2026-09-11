from django.contrib import admin
from .models import globe_employee,DEL_pass,CCU_pass,BOM_pass
from django.contrib.auth.models import User,Group
# Register your models here.

admin.site.register(globe_employee)
admin.site.unregister(User)
admin.site.unregister(Group)
admin.site.register(DEL_pass)
admin.site.register(BOM_pass)
admin.site.register(CCU_pass)