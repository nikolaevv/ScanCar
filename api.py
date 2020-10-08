# -*- coding: utf8 -*-

from flask import Flask, render_template, send_from_directory, session, redirect, url_for, escape, request
from flask_sqlalchemy import SQLAlchemy
from app import models, app, db
#from werkzeug.utils import secure_filename
import os

@app.route('/', methods = ['POST'])
def scan_photo():
    if request.method == 'POST':
        photo = request.form['new_exercise']