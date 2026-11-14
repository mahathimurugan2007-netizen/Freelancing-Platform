from django.db import models
import uuid
from django.utils import timezone
class User_Detail(models.Model):
	name = models.CharField(max_length=100)
	mobile = models.CharField(max_length=20)
	username = models.CharField(max_length=100,unique=True)
	password = models.CharField(max_length=100)
	email = models.EmailField(max_length=100)
	bio = models.TextField(max_length=2000,null=True,blank=True)
	image = models.FileField('Upload Image',upload_to='',null=True)
	address = models.TextField(max_length=2000)
	def __str__(self):
		return self.username
class Editor_Detail(models.Model):
	name = models.CharField(max_length=100)
	mobile = models.CharField(max_length=20)
	username = models.CharField(max_length=100,unique=True)
	password = models.CharField(max_length=100)
	email = models.EmailField(max_length=100)
	bio = models.TextField(max_length=2000,null=True,blank=True)
	image = models.FileField('Upload Image',upload_to='',null=True)
	address = models.TextField(max_length=2000)
	def __str__(self):
		return self.username
class File_Type(models.Model):
	user_id = models.ForeignKey(Editor_Detail, on_delete=models.CASCADE)
	title = models.CharField(max_length=500)
	category = models.CharField(max_length=100)
	price = models.CharField(max_length=500,null=True,blank=True)
	time = models.CharField(max_length=100,null=True,blank=True)
	sdate = models.DateField(null=True,blank=True)
	edate = models.DateField(null=True,blank=True)
	image = models.FileField('Upload Image',upload_to='',null=True)
	project_type = models.CharField(max_length=100,null=True,blank=True)
	description = models.TextField(max_length=2000)
	def __str__(self):
		return self.title

class FreelancerProfile(models.Model):
	user_id = models.ForeignKey(User_Detail, on_delete=models.CASCADE)
	biography = models.TextField(max_length=2000)
	skills = models.CharField(max_length=2000)
	experience = models.TextField()
	portfolio_link = models.CharField(max_length=255)
	availability = models.CharField(max_length=20)

	def __str__(self):
		return f"{self.user_id.name}"
class RequestProject(models.Model):
	user_id = models.ForeignKey(Editor_Detail, on_delete=models.CASCADE)
	job_id = models.ForeignKey(File_Type, on_delete=models.CASCADE)
	freelancer_id = models.ForeignKey(User_Detail, on_delete=models.CASCADE)
	job_status = models.CharField(max_length=100)
	msg = models.TextField()
	reply = models.TextField(null=True,blank=True)
	delivery_date = models.DateField(null=True,blank=True)
	project_status = models.CharField(max_length=100,null=True,blank=True)
	def __str__(self):
		return f"{self.job_id.title}"
class Payment(models.Model):
	req_id = models.ForeignKey(RequestProject, on_delete=models.CASCADE)
	payment_amount = models.CharField(max_length=100)
	payment_status = models.CharField(max_length=100)
	payment_date = models.DateField()
	def __str__(self):
		return f"{self.req_id.job_id.title}"
