from django.db import models

# Create your models here.


class File(models.Model):
	path = models.FilePathField()


class UserLang(models.Model):
	LANGUAGES = (
		('EN', 'English'),
		('RU', 'Russian')
	)
	user_id = models.CharField(blank=False, max_length=24, unique=True)
	language = models.CharField(max_length=2, choices=LANGUAGES, default='EN')
	files = models.ManyToManyField(File)
