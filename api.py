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
import time

ALLOWED_EXTENSIONS = {'jpg', 'jpeg'}
headers = {'X-IBM-Client-Id': token, 'content-type': "application/json", 'accept': "application/json"}

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
        return None

def zip_image(image):
    # Алгоритм сжатия фото
    im1 = Image.open(image)
    #image = Image.open(image)
    #image.save(image.path, quality = 20, optimize = True) 
    im1 = im1.resize((720, 1080), Image.ANTIALIAS)
    im1.save('./photos/image_scaled.jpg', quality = 60)
    return open('./photos/image_scaled.jpg', 'rb')

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

        return {'title': favourite, 'brand': brand, 'model': model, 'poster': image_url}
    return {'error': 'Invalid type of photo'}, status.HTTP_400_BAD_REQUEST
    return {'error': 'Some data is missing'}, status.HTTP_400_BAD_REQUEST

@app.route('/api/auto/get', methods = ['GET'])
def get_auto():
    # Получение авто по марке
    

    if request.form.get('brand', None) is not None and request.form.get('model', None) is not None and request.form.get('num', None) is not None and request.form.get('offset', None) is not None:

        title = request.form['brand']
        car_model = request.form['model']

        start_price, end_price = 0, 900000000

        if request.form.get('start_price', None) is not None:
            start_price = int(request.form['start_price'])
        if request.form.get('end_price', None) is not None:
            end_price = int(request.form['end_price'])

        response = requests.get('https://gw.hackathon.vtb.ru/vtb/hackathon/marketplace', headers = headers).json()
        offers = response['list']
        # Запрос к VTB-API

        cars_vtb = []

        for brand in offers:
            if brand['title'] == title:
                cars_vtb += [model for model in brand['models'] if (model['model']['title'] == car_model and model['minprice'] > start_price)]

        print(cars_vtb)
        return {'vtb': cars_vtb, 'autoru': []}


    return {'error': 'Some data is missing'}, status.HTTP_400_BAD_REQUEST


#print(get_poster('LADA', 'Granta'))
app.secret_key = os.urandom(24)
app.run(host='0.0.0.0', port='80', debug=True)