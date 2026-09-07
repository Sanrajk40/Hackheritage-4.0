from django.db import models

# Create your models here.
class globe_employee(models.Model):
    name= models.CharField(max_length=100)
    empid = models.CharField(max_length=50)
    airport_no =models.CharField(max_length=10)
    active_status = models.BooleanField(default=False)
    password = models.CharField()
