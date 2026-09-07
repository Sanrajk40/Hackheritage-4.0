from django.db import models

# Create your models here.
class globe_employee(models.Model):
    name= models.CharField(max_length=100)
    empid = models.CharField(max_length=50)
    airport_no =models.CharField(max_length=100)
    active_status = models.BooleanField(default=False)
    mail =models.CharField(default='k@gmail.com')
    password = models.CharField(default='smp')
