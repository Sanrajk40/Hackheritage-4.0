from django.db import models

# Create your models here.
class globe_employee(models.Model):
    name= models.CharField(max_length=100)
    empid = models.CharField(max_length=50)
    airport_no =models.CharField(max_length=100)
    active_status = models.BooleanField(default=False)
    mail =models.CharField(default='k@gmail.com')
    password = models.CharField(default='smp')

class DEL_pass(models.Model):
    empid = models.CharField(max_length=50)
    empname = models.CharField(max_length=50)
    pass_name = models.CharField(max_length=100)
    passport_no=models.CharField(max_length=50)
    visa_no= models.CharField(max_length=50)
    nationality = models.CharField(max_length=60)

class BOM_pass(models.Model):
    empid = models.CharField(max_length=50)
    empname = models.CharField(max_length=50)
    pass_name = models.CharField(max_length=100)
    passport_no=models.CharField(max_length=50)
    visa_no= models.CharField(max_length=50)
    nationality = models.CharField(max_length=60)

class CCU_pass(models.Model):
    empid = models.CharField(max_length=50)
    empname = models.CharField(max_length=50)
    pass_name = models.CharField(max_length=100)
    passport_no=models.CharField(max_length=50)
    visa_no= models.CharField(max_length=50)
    nationality = models.CharField(max_length=60)
