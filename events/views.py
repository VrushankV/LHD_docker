from django.shortcuts import render, redirect
from predicthq import Client
from django.http import HttpResponse
import requests
from events.models import SafeLocation, DangerLocation, HelpLocation, Event\
							,UserComments

# Create your views here.

def index(request):

	url = "https://api.predicthq.com/v1/events/"
	ACCESS_TOKEN = "h8jTYSTHTta2o84n9WfahbIO2eRC9S"
	payload={
	'sort':'rank',
	'count':'50',
	'category' : 'disasters',
	'labels' : ['disaster','fire']
	}
	headers={
	'Accept': 'application/json',
	'Authorization': "Bearer " + ACCESS_TOKEN
	}
	r = requests.get(url, params=payload,headers=headers)
	# phq = Client(access_token=ACCESS_TOKEN)
	results = r.json()['results']
	#print(results)
	count = 0
	for i in results:
		
		
		if 'vehicle-accident' in i['labels']:
			results.pop(count)

		
		count = count + 1

	for i in results:
		print(i)
		print("*"*100)	
	# for event in phq.events.search(category="disasters",state="active"):
	#     print(event.description, event.category, event.title, event.start.strftime('%Y-%m-%d'))
	return render(request,'listOfEvents.html',{'events':results})

def eventDetail(request,eventId):
	url = "https://api.predicthq.com/v1/events/"
	ACCESS_TOKEN = "h8jTYSTHTta2o84n9WfahbIO2eRC9S"
	payload={
	'id' : eventId
	}
	headers={
	'Accept': 'application/json',
	'Authorization': "Bearer " + ACCESS_TOKEN
	}
	r = requests.get(url, params=payload,headers=headers)
	#print(eventId)
	results = r.json()['results']
	print(results)
	results = results[0]
	longi = results['location'][0]
	lat = results['location'][1]
	api = "147b79daa29884e1dab8fac91b7526d6"
	print(type(lat))
	url = "http://api.openweathermap.org/data/2.5/weather?lat="+str(lat)+"&lon="+str(longi)+"&appid="+api;
	response = requests.get(url)
	print(type(response))
	print(response.text)
	res = response.json()
	print(lat,longi)
	#print(data)
	temp = res['main']['temp']
	pressure = res['main']['pressure']
	humidity = res['main']['humidity']
	temp_min = res['main']['temp_min']
	temp_max = res['main']['temp_max']
	windspeed = res['wind']['speed']
	try:
		winddeg = res['wind']['deg']
	except:
		winddeg = None	
	mainweather	= res['weather'][0]['main']
	description = res['weather'][0]['description']

	print(temp)
	print(mainweather)
	print(description)
	safeLocation = []
	dangerLocation = []
	helpLocation = []

	safeObj = SafeLocation.objects.all().filter(eventId=eventId)
	dangerObj = DangerLocation.objects.all().filter(eventId=eventId)
	helpObj = HelpLocation.objects.all().filter(eventId=eventId)

	try:
		obj = Event.objects.get(eventId=eventId)
	except:
		obj = Event.objects.create(eventId=eventId)
		obj.save()

	comments = UserComments.objects.all().filter(eventId=eventId)
	print(type(comments))
	
	print(results['id'])

	return render(request,'eventDetail.html',{'event':results,
											  'weather':[mainweather,description],
											  'temp':temp,
											  'pressure':pressure,
											  'humidity':humidity,
											  'windspeed':windspeed,
											  'winddeg': winddeg,
											  'safeLocation':safeLocation,
											  'dangerLocation': dangerLocation,
											  'helpLocation': helpLocation,
											  'comments': comments,
												})

def mapMarker(request):
	lat = request.POST.get('lat')
	lng = request.POST.get('lng')
	eventId = request.POST.get('eventId')
	color = request.POST.get('colour')
	print(request.POST)
	print(request.user)
	if request.user:
		if color == '0':
			obj = Event.objects.get(eventId=eventId)
			obj = HelpLocation.objects.create(eventId=obj,
										latitude=lat,
										longitude=lng)
			obj.save()
		if color == '1':
			print('Red')
			obj = Event.objects.get(eventId=eventId)
			obj = DangerLocation.objects.create(eventId=obj,
										latitude=lat,
										longitude=lng)
			obj.save()
		if color == '2':
			obj = Event.objects.get(eventId=eventId)
			obj = SafeLocation.objects.create(eventId=obj,
										latitude=lat,
										longitude=lng)
			obj.save()	
				
	#SafeLocation.objects.create()
	return HttpResponse("Done")

def comments(requests):
	print(requests.POST)
	eventId = requests.POST.get('eventId')
	comment = requests.POST.get('comment')
	eventObj = Event.objects.get(eventId=eventId)

	commObj = UserComments.objects.create(userName=requests.user,eventId=eventObj,userComment=comment)
	commObj.save()
	return redirect("/events/"+eventId)

