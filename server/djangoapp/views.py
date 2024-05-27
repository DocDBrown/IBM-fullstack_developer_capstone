# Uncomment the required imports before adding the code
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from datetime import datetime
from django.http import JsonResponse
import logging
import json
from django.views.decorators.csrf import csrf_exempt
from .populate import initiate
from django.contrib.auth import login, logout, authenticate
from .models import CarMake, CarModel
from .restapis import get_request, analyze_review_sentiments, post_review
import requests

# Get an instance of a logger
logger = logging.getLogger(__name__)

# Create a `login_request` view to handle sign in request
@csrf_exempt
def login_user(request):
    data = json.loads(request.body)
    username = data['userName']
    password = data['password']
    user = authenticate(username=username, password=password)
    data = {"userName": username}
    if user is not None:
        login(request, user)
        data = {"userName": username, "status": "Authenticated"}
    return JsonResponse(data)

@csrf_exempt  
def logout_request(request):
    logger.info("Logout request received")
    if request.user.is_authenticated:
        logger.info(f"User {request.user.username} is logging out")
        try:
            logout(request)
            logger.info("User logged out successfully")
            response = HttpResponseRedirect('/')
            return JsonResponse(data)
        except Exception as e:
            logger.error(f"Error during logout: {e}")
            return JsonResponse({"error": str(e)}, status=500)
    else:
        logger.warning("Logout request received but no user is logged in")
        return JsonResponse({"error": "No user logged in"}, status=400)

@csrf_exempt
def registration(request):
    context = {}
    data = json.loads(request.body)
    username = data['userName']
    password = data['password']
    first_name = data['firstName']
    last_name = data['lastName']
    email = data['email']
    username_exist = False
    email_exist = False
    try:
        User.objects.get(username=username)
        username_exist = True
    except:
        logger.debug("{} is new user".format(username))

    if not username_exist:
        user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,password=password, email=email)
        login(request, user)
        data = {"userName":username,"status":"Authenticated"}
        return JsonResponse(data)
    else :
        data = {"userName":username,"error":"Already Registered"}
        return JsonResponse(data)

def get_cars(request):
    count = CarMake.objects.filter().count()
    print(count)
    if(count == 0):
        initiate()
    car_models = CarModel.objects.select_related('car_make')
    cars = []
    for car_model in car_models:
        cars.append({"CarModel": car_model.name, "CarMake": car_model.car_make.name})
    return JsonResponse({"CarModels":cars})

def get_dealerships(request, state="All"):
    if(state == "All"):
        endpoint = "/fetchDealers"
    else:
        endpoint = "/fetchDealers/"+state
    dealerships = get_request(endpoint)
    return JsonResponse({"status":200,"dealers":dealerships})

def get_dealer_details(request, dealer_id):
    if dealer_id:
        endpoint = "/fetchDealer/" +str(dealer_id)
        try:
            response = requests.get(endpoint)
            response.raise_for_status()  
            dealerships = response.json()
            return JsonResponse({"status": 200, "dealers": dealerships})
        except requests.exceptions.RequestException as e:
            return JsonResponse({"status": 500, "error": str(e)}, status=500)
    else:
        return JsonResponse({"status": 400, "error": "Invalid dealer ID"}, status=400)

def get_dealer_reviews(request, dealer_id):
    if dealer_id:
        endpoint = "/fetchReviews/dealer/" +str(dealer_id)
        try:
            reviews = get_request(endpoint)
            for review_detail in reviews:
                response = analyze_review_sentiments(review_detail['review'])
                print(response)
                review_detail['sentiment'] = response['sentiment']
            return JsonResponse({"status":200,"reviews":reviews})
        except requests.exceptions.RequestException as e:
            return JsonResponse({"status": 500, "error": str(e)}, status=500)
    else:
        return JsonResponse({"status": 400, "error": "Invalid dealer ID"}, status=400)

def add_review(request):
    if(request.user.is_anonymous == False):
        data = json.loads(request.body)
        try:
            response = post_review(data)
            return JsonResponse({"status":200})
        except:
            return JsonResponse({"status":401,"message":"Error in posting review"})
    else:
        return JsonResponse({"status":403,"message":"Unauthorized"})