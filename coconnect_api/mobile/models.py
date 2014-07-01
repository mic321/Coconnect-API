## from django.db import models
from django.contrib.gis.db import models
from django.db.models.signals import post_save
from django.contrib.auth import get_user_model
from django.dispatch import receiver

from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User

# Create your models here.

@receiver(post_save, sender = get_user_model())
def create_auth_token(sender, instance = None, created = False, **kwargs):
	if created:
		Token.objects.create(user = instance)

class Company(models.Model):
	name = models.CharField(max_length = 200)
	user = models.ManyToManyField(User)

class Title(models.Model):
	title = models.CharField(max_length = 200)
	user = models.ManyToManyField(User)

class Industry(models.Model):
	industry = models.CharField(max_length = 200)
	user = models.ManyToManyField(User)

class Headline(models.Model):
	headline = models.CharField(max_length = 200)
	user = models.OneToOneField(User, primary_key = True)

class Geolocation(models.Model):
	position = models.PointField(geography = True)
	created = models.DateTimeField(auto_now_add = True)
	user = models.ForeignKey(User)
	objects = models.GeoManager()


# INSERT INTO mobile_geolocation (position, user_id) VALUES (ST_GeographyFromText('SRID=4326;POINT(-5 10)'), 1);

# SELECT user_id FROM mobile_geolocation WHERE ST_DWithin(position, ST_GeographyFromText('SRID=4326;POINT(-5 5)'), 1);