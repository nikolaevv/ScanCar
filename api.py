# -*- coding: utf8 -*-

from flask import Flask, render_template, send_from_directory, session, redirect, url_for, escape, request, Response
from flask_sqlalchemy import SQLAlchemy
from app import models, app, db
from flask_api import status
#import StringIO
from PIL import Image
from werkzeug.utils import secure_filename
#import pandas
import os
from config import token
import base64
import requests
import json
import time

from sqlalchemy.ext.declarative import DeclarativeMeta

ALLOWED_EXTENSIONS = {'jpg', 'jpeg'}
headers = {'X-IBM-Client-Id': token, 'content-type': "application/json", 'accept': "application/json"}

def queryset_to_list(queryset):
    flat_list = []
    for q in queryset:
        q_dict = q.__dict__
        del q_dict['_sa_instance_state']
        del q_dict['description']
        q_dict['type'] = 'autoru'
        flat_list.append(q_dict)
    return flat_list

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def get_poster(title, auto_model):
    response = requests.get('https://gw.hackathon.vtb.ru/vtb/hackathon/marketplace', headers = headers).json()
    offers = response['list']
    # Запрос к VTB-API

    cars_vtb = []
    print(offers)

    for brand in offers:
        if brand['title'] == title:
            cars_vtb += [model['bodies'][0]['photo'] for model in brand['models'] if (model['model']['title'] == auto_model and len(model['bodies'][0]) > 0)]
    
    if len(cars_vtb) > 0:
        return cars_vtb[0]
    else:
        cars = models.Car.query.filter(models.Car.brand == title).filter(models.Car.model == auto_model).all()
        if len(cars) > 0:
            return cars[0].image_url

def zip_image(image):
    # Алгоритм сжатия фото
    im1 = Image.open(image)
    #image = Image.open(image)
    #image.save(image.path, quality = 20, optimize = True) 
    im1 = im1.resize((720, 1080), Image.ANTIALIAS)
    im1.save('./photos/image_scaled.jpg', quality = 60)
    return open('./photos/image_scaled.jpg', 'rb')

def get_year(title, auto_model):
    cars = models.Car.query.filter(models.Car.brand == title).filter(models.Car.model == auto_model).all()
    if len(cars) > 0:
        return cars[0].production_date
    else:
        return 2020

@app.route('/api/photo/recognize', methods = ['POST'])
def scan_photo():
    # Распознавание одного фото
    photo = request.files['photo']
    
    if photo and allowed_file(photo.filename):
        #with open("my_image.jpg", "rb") as img_file:
        photo = zip_image(photo)
        my_string = base64.b64encode(photo.read())
        # Преобразование в base-64
        
    
        try:
            response = requests.post('https://gw.hackathon.vtb.ru/vtb/hackathon/car-recognize', headers = headers, json = {'content': str(my_string, 'utf-8')}).json()
            # Запрос к VTB-API
            print(response)
            
            probabilities = response['probabilities']
            print(probabilities)
            favourite = max(probabilities, key = probabilities.get)
            print(favourite)
            # Фаворит нейросети ВТБ
        except Exception:
            return {'error': 'Photo was not recognized'}, status.HTTP_400_BAD_REQUEST

        brand, model = favourite.split()[0], favourite.split()[-1]
        image_url = get_poster(brand, model)

        return {'title': favourite, 'brand': brand, 'model': model, 'poster': image_url, 'year': get_year(brand, model)}
        # 'year': get_year(brand, model)
    return {'error': 'Invalid type of photo'}, status.HTTP_400_BAD_REQUEST
    return {'error': 'Some data is missing'}, status.HTTP_400_BAD_REQUEST

@app.route('/api/auto/get', methods = ['POST'])
def get_auto():
    # Получение авто по марке
    #print(request.get_json())
    if request.get_json() is not None:
        if request.get_json().get('brand', None) is not None and request.get_json().get('model', None) is not None and request.get_json().get('num', None) is not None and request.get_json().get('offset', None) is not None:

            title = request.get_json()['brand']
            car_model = request.get_json()['model']

            start_price, end_price = 0, 900000000

            if request.get_json().get('start_price', None) is not None:
                start_price = int(request.get_json()['start_price'])
            if request.get_json().get('end_price', None) is not None:
                end_price = int(request.get_json()['end_price'])

            response = requests.get('https://gw.hackathon.vtb.ru/vtb/hackathon/marketplace', headers = headers).json()
            offers = response['list']
            # Запрос к VTB-API

            cars_vtb = []

            for brand in offers:
                if brand['title'] == title:
                    cars_vtb += [{'brand': title, 'model': car_model, 'image_url': get_poster(title, car_model), 'price': model['minprice'], 'production_date': 2020, 'type': 'vtb'} 
                                for model in brand['models'] 
                                if (model['model']['title'] == car_model and model['minprice'] > start_price and model['minprice'] < end_price)]

            print(cars_vtb)
            offset = int(request.get_json()['offset'])
            num = int(request.get_json()['num'])

            cars_autoru = queryset_to_list(models.Car.query.filter(models.Car.brand == title).filter(models.Car.model == car_model).all())
            #[offset:num]
            cars = cars_vtb + cars_autoru
            

            return {'cars': cars[offset:num]}
        return {'error': 'Some data is missing'}, status.HTTP_400_BAD_REQUEST
    return {'error': 'Some data is missing'}, status.HTTP_400_BAD_REQUEST

@app.route('/api/auto/get', methods = ['GET'])
def calc_auto():
    pass


#print(get_poster('LADA', 'Granta'))
app.secret_key = os.urandom(24)
app.run(host='0.0.0.0', port='80', debug=True)