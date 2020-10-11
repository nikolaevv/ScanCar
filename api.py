# -*- coding: utf8 -*-

from flask import Flask, render_template, send_from_directory, session, redirect, url_for, escape, request, Response
from flask_sqlalchemy import SQLAlchemy
from app import models, app, db
from flask_api import status
#import StringIO
from PIL import Image
from werkzeug.utils import secure_filename
#import pandas
import pandas as pd
#import tensorflow as tf
#import keras
#from keras.models import load_model
import os
from config import token
import numpy as np
import base64
import datetime
import requests
import json
import time

#from sqlalchemy.ext.declarative import DeclarativeMeta

# we need to redefine our metric function in order 
# to use it when loading the model 
def auc(y_true, y_pred):
    auc = tf.metrics.auc(y_true, y_pred)[1]
    keras.backend.get_session().run(tf.local_variables_initializer())
    return auc

#global graph
#graph = tf.get_default_graph()
#model = load_model('my_model', custom_objects={'auc': auc})

ALLOWED_EXTENSIONS = {'jpg', 'jpeg'}
headers = {'X-IBM-Client-Id': token, 'content-type': "application/json", 'accept': "application/json"}

def queryset_to_list(queryset):
    flat_list = []
    for q in queryset:
        q_dict = q.__dict__
        del q_dict['_sa_instance_state']
        del q_dict['description']
        q_dict['type'] = 'autoru'
        images = [q_dict['image_url_1'], q_dict['image_url_2'], q_dict['image_url_3']]
        q_dict['image_urls'] = [i for i in images if i is not None]
        del q_dict['image_url_1']
        del q_dict['image_url_2']
        del q_dict['image_url_3']
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
            return cars[0].image_url_1

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

def priced(model, start_price, end_price):
    # Соответствие цене
    if model.get('minprice', None) is not None:
        return model['minprice'] > start_price and model['minprice'] < end_price
    else:
        return True

def get_price(model):
    if model.get('minprice', None) is not None:
        return model['minprice']
    else:
        return '-'

def predict(photo):
    data = {"success": False}

    #params = flask.request.json
    #if (params == None):
    #params = flask.request.args

    # if parameters are found, return a prediction
    #if (params != None):
    #x=pd.DataFrame.from_dict(params, orient='index').transpose()
    with graph.as_default():
        print(model.predict(photo))
        data["prediction"] = str(model.predict(photo)[0][0])
        data["success"] = True

    # return a response in json format 
    return flask.jsonify(data)

@app.route('/api/specials/get', methods = ['GET'])
def get_settings():
    response = requests.get('https://gw.hackathon.vtb.ru/vtb/hackathon/settings?name=Haval&language=ru-RU', headers = headers).json()
    return {'specialConditions': response['specialConditions']}

@app.route('/api/photo/recognize', methods = ['POST'])
def scan_photo():
    from custom_predict import load_and_preprocess_image, lite_model
    # Распознавание одного фото
    photo = request.files['photo']
    
    if photo and allowed_file(photo.filename):
        #with open("my_image.jpg", "rb") as img_file:
        photo = zip_image(photo)
        my_string = base64.b64encode(photo.read())
        # Преобразование в base-64
        
        #predict(photo)
        custom_marks = ['skoda octavia', 'volkswagen polo', 'KIA RIO', 'HYUNDAI SOLARIS', 'volkswagen tiguan']
    
        input_arr = load_and_preprocess_image('./photos/image_scaled.jpg')
        probs_lite = lite_model(input_arr[None, ...])[0]
        favourite = custom_marks[probs_lite.tolist().index(max(probs_lite))]

        if np.argmax(probs_lite) < 1:
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
            print(response)
            offers = response['list']
            # Запрос к VTB-API
            print(offers)

            cars_vtb = []

            for brand in offers:
                if brand['title'] == title:
                    cars_vtb += [{'brand': title, 'model': car_model, 'image_urls': [get_poster(title, car_model)], 'price': get_price(model), 'bodywork': model['bodies'][0]['typeTitle'], 'color': '-', 'engine': '-', 'tax': '-', 'kpp': '-', 'AWD': '-', 'steering_wheel': '-', 'customs': '-', 'production_date': 2020, 'type': 'vtb'} 
                                for model in brand['models'] 
                                if (model['model']['title'] == car_model and priced(model, start_price, end_price) is True)]

            print(cars_vtb)
            offset = int(request.get_json()['offset'])
            num = int(request.get_json()['num'])

            cars_autoru = queryset_to_list(models.Car.query.filter(models.Car.brand == title).filter(models.Car.model == car_model).all())
            #[offset:num]
            cars = cars_vtb + cars_autoru

            return {'cars': cars[offset:(offset+num)]}
        return {'error': 'Some data is missing'}, status.HTTP_400_BAD_REQUEST
    return {'error': 'Some data is missing'}, status.HTTP_400_BAD_REQUEST

@app.route('/api/credit/calc', methods = ['POST'])
def calc_auto():
    print(request.get_json())
    if request.get_json() is not None:
        if request.get_json().get('cost', None) is not None and request.get_json().get('initialFee', None) is not None and request.get_json().get('kaskoValue', None) is not None and request.get_json().get('term', None) is not None:

            cost = int(request.get_json()['cost'])
            initialFee = int(request.get_json()['initialFee'])
            kaskoValue = int(request.get_json()['kaskoValue'])
            term = int(request.get_json()['term'])
            specialConditions = request.get_json()['specialConditions']

            data = {'clientTypes': ['ac43d7e4-cd8c-4f6f-b18a-5ccbc1356f75'], 
                    'cost': float(cost), 
                    'initialFee': float(initialFee), 
                    'kaskoValue': kaskoValue, 
                    'term': term, 
                    'residualPayment': float(cost - initialFee), 
                    'language': 'ru-RU',
                    'settingsName': 'Haval',
                    'specialConditions': specialConditions
            }

            try:
                response = requests.post('https://gw.hackathon.vtb.ru/vtb/hackathon/calculate', headers = headers, json = data).json()
                program = response['result']
                return program
            except Exception:
                # Заглушка
                return {"contractRate": 10.1,
                        "kaskoCost": 10000,
                        "lastPayment": 45.98839406,
                        "loanAmount": 1000000,
                        "payment": 50000,
                        "subsidy": 88.7185816,
                        "term": 5}
        return {'error': 'Some data is missing'}, status.HTTP_400_BAD_REQUEST
    return {'error': 'Some data is missing'}, status.HTTP_400_BAD_REQUEST

@app.route('/api/credit/apply', methods = ['POST'])
def apply_for_credit():
    if request.get_json() is not None:
        if request.get_json().get('comment', None) is not None and request.get_json().get('email', None) is not None and request.get_json().get('income_amount', None) is not None and request.get_json().get('birth_date_time', None) is not None and request.get_json().get('birth_place', None) is not None and request.get_json().get('family_name', None) is not None and request.get_json().get('first_name', None) is not None and request.get_json().get('gender', None) is not None and request.get_json().get('middle_name', None) is not None and request.get_json().get('nationality_country_code', None) is not None:
            comment = request.get_json()['comment']
            email = request.get_json()['email']
            income_amount = int(request.get_json()['income_amount'])
            birth_date_time = request.get_json()['birth_date_time']
            birth_place = request.get_json()['birth_place']
            family_name = request.get_json()['family_name']
            first_name = request.get_json()['first_name']
            gender = request.get_json()['gender']
            middle_name = request.get_json()['first_name']

            phone = request.get_json()['phone']
            interest_rate = float(request.get_json()['interest_rate'])
            requested_amount = int(request.get_json()['requested_amount'])
            requested_term = int(request.get_json()['requested_term']) * 12
            trade_mark = request.get_json()['trade_mark']
            vehicle_cost = int(request.get_json()['vehicle_cost'])
            
            nationality_country_code = request.get_json()['nationality_country_code']

            data = {'comment': comment, 
                    'customer_party': {'email': email,
                                       'income_amount': income_amount,
                                       'person': {'birth_date_time': birth_date_time,
                                                  'birth_place': birth_place,
                                                  'family_name': family_name,
                                                  'first_name': first_name,
                                                  'middle_name': middle_name,
                                                  'gender': gender,
                                                  'nationality_country_code': nationality_country_code
                                        },
                                        'phone': phone,
                    }, 
                    
                    "interest_rate": interest_rate,
                    "requested_amount": requested_amount,
                    "requested_term": requested_term,
                    "trade_mark": trade_mark,
                    "vehicle_cost": vehicle_cost
            }

            #"datetime": datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ'),
            response = requests.post('https://gw.hackathon.vtb.ru/vtb/hackathon/carloan', headers = headers, json = data).json()
        
            return {'approved': response['application']['decision_report']['application_status'] == 'prescore_approved', 'decision_end_date': response['application']['decision_report']['decision_end_date']}
        return {'error': 'Some data is missing'}, status.HTTP_400_BAD_REQUEST
    return {'error': 'Some data is missing'}, status.HTTP_400_BAD_REQUEST

app.secret_key = os.urandom(24)
app.run(host='0.0.0.0', port='80', debug=True)