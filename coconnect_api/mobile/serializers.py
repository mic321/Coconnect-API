from rest_framework import serializers

from django.contrib.auth.models import User
from mobile.models import Geolocation

class UserSerializer(serializers.Serializer):
	username = serializers.CharField(max_length = 200)
	password = serializers.CharField(max_length = 200)
	email = serializers.EmailField(max_length = 75)
	first_name = serializers.CharField(max_length = 200)
	last_name = serializers.CharField(max_length = 200)

# ## Not sure how conversion of field to geography type works with serializer
# class GeolocationSerializer(serializers.ModelSerializer):
# 	class Meta:
# 		model = Geolocation