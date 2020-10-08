# -*- coding: utf8 -*-

from flask import Flask, render_template, send_from_directory, session, redirect, url_for, escape, request
from flask_sqlalchemy import SQLAlchemy
from app import models, app, db
from flask_api import status
from werkzeug.utils import secure_filename
import os
from config import token
import base64
import requests
import time

ALLOWED_EXTENSIONS = {'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/api/photo/recognize', methods = ['POST'])
def scan_photo():
    # Распознавание одного фото

    photo = request.files['photo']
    print(photo)

    if photo and allowed_file(photo.filename):
        #with open("my_image.jpg", "rb") as img_file:
        my_string = base64.b64encode(photo.read())
        # Преобразование в base-64
        headers = {'X-IBM-Client-Id': token, 'content-type': "application/json", 'accept': "application/json"}
    
        try:
            response = requests.post('https://gw.hackathon.vtb.ru/vtb/hackathon/car-recognize', headers = headers, json = {'content': str(my_string, 'utf-8')}).json()
            # Запрос к VTB-API
            
            probabilities = response['probabilities']
            favourite = max(probabilities, key = probabilities.get)
            # Фаворит нейросети ВТБ
        except Exception:
            return {'error': 'Photo was not recognized'}, status.HTTP_400_BAD_REQUEST

        return favourite
    return {'error': 'Invalid type of photo'}, status.HTTP_400_BAD_REQUEST
        

app.secret_key = os.urandom(24)
app.run(debug=True)