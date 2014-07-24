from django.http import HttpResponse
from django.contrib.auth.models import User

from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import exception_handler

from mobile.serializers import UserSerializer #, GeolocationSerializer
from mobile.models import Company, Title, Industry, Headline, Geolocation

from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import D

from django.db.utils import IntegrityError

import sys, datetime

@api_view(['POST'])
def registerUser(request):
	"""
	Register a new user
	"""

	serializer = UserSerializer(data = request.DATA)
	if serializer.is_valid():
		try:
			User.objects.create_user(
				email = serializer.init_data['email'],
				username = serializer.init_data['username'],
				password = serializer.init_data['password'],
				first_name = serializer.init_data['first_name'],
				last_name = serializer.init_data['last_name']
			)
			## I believe Django's signals are handled synchronously so the token should be created by now
			token = Token.objects.filter(user__username = serializer.data['username'])[0]	
		except IntegrityError as e:
			return Response(data = {'details': 'IntegrityError: Username likely already exists'}, status = status.HTTP_400_BAD_REQUEST)
		except:
			e = sys.exc_info()[0]
			return Response(data = {'details': str(e)}, status = status.HTTP_400_BAD_REQUEST)
		return Response(
			data = {'token': token.key}, 
			status = status.HTTP_201_CREATED,
			headers = {'Access-Control-Allow-Origin': '*'})
	else:
		return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
@authentication_classes((TokenAuthentication, ))
@permission_classes((IsAuthenticated, ))
def userProfile(request):
	"""
	Retrieve, create or update user profile
	"""
	user = request.user
	if request.method == 'GET':
		data_response = {
			'company': '',
			'industry': '',
			'title': '',
			'headline': '' }
		c = Company.objects.filter(user = user)
		t = Title.objects.filter(user = user)
		i = Industry.objects.filter(user = user)	
		h = Headline.objects.filter(user = user)	

		if c.exists():
			data_response['company'] = c[0].name
		if t.exists():
			data_response['title'] = t[0].title 
		if i.exists():
			data_response['industry'] = i[0].industry 
		if h.exists():
			data_response['headline'] = h[0].headline 

		return Response(
			data = data_response,
			status = status.HTTP_200_OK,
			headers = {'Access-Control-Allow-Origin': '*'})
	
	elif request.method == 'POST':
		
		company 	= request.DATA.get('company', None)
		title 		= request.DATA.get('title', None)
		industry 	= request.DATA.get('industry', None)
		headline 	= request.DATA.get('headline', None)
		
		respondToPOST(Company, user.company_set, company, 'name', user)
		respondToPOST(Title, user.title_set, title, 'title', user)
		respondToPOST(Industry, user.industry_set, industry, 'industry', user)
		
		## Update user's headline data independently because Headline objects have
		## a one to one relationship with user
		try:
			if hasattr(user, 'headline'):
				user.headline.delete()
			if headline:
				h = Headline(headline = headline, user = user)
				h.save()
		except:
			e = sys.exc_info()[0]
			return Response(data = {'details': str(e)}, status = status.HTTP_400_BAD_REQUEST)
		return Response(data = {'details': 'Success'},
			status = status.HTTP_200_OK,
			headers = {'Access-Control-Allow-Origin': '*'})

	
def respondToPOST(profile_class, associated_manager, user_input, model_field, user):
	## First remove any prior user profile associations
	if associated_manager.all().exists():
		associated_manager.remove(associated_manager.all()[0]) ## Remove the prior association between user and company
	## Second add new profile association if necessary
	if user_input:
		qs = profile_class.objects.filter(**{model_field: user_input})
		if not qs.exists():
			company_obj = profile_class(**{model_field: user_input})
			company_obj.save()
		else:
			company_obj = qs[0]
		company_obj.user.add(user)


@api_view(['POST'])
@authentication_classes((TokenAuthentication, ))
@permission_classes((IsAuthenticated, ))
def recordPlace(request):
	"""Record a user's location"""
	latitude = request.DATA['latitude']
	longitude = request.DATA['longitude']
	geo = GEOSGeometry('POINT(%s %s)' % (latitude, longitude))
	if geo:
		g = Geolocation(position = geo, user = request.user)
		g.save()
		return Response(
			status = status.HTTP_201_CREATED,
			headers = {'Access-Control-Allow-Origin': '*'})
	else:
		return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@authentication_classes((TokenAuthentication, ))
@permission_classes((IsAuthenticated, ))
def recordTime(request):
	"""Record the time at which a user interacts with the app"""
	pass


@api_view(['GET'])
@authentication_classes((TokenAuthentication, ))
@permission_classes((IsAuthenticated, ))
def getUsersInProximity(request):
	"""Return the users in the user's proximity"""
	
	latitude = request.DATA['latitude']
	longitude = request.DATA['longitude']
	my_geo = GEOSGeometry('POINT(%s %s)' % (latitude, longitude))
	
	qs_nearby_geos = Geolocation.objects.filter(position__distance_lte = (my_geo, D(m=16000)))
	nearby_user_ids = []
	for geo in qs_nearby_geos:
		nearby_user_ids.append(geo.user.id)
	qs = User.objects.filter(
		geolocation__created__gte = datetime.datetime.now() - datetime.timedelta(hours = 1)
	).filter(
		pk__in = nearby_user_ids
	)
	
	peoples = [ {'first_name': r.first_name, 'last_name':r.last_name} for r in qs]
	return Response(
		data = {'people': peoples},
		status = status.HTTP_201_CREATED,
		headers = {'Access-Control-Allow-Origin': '*'})
