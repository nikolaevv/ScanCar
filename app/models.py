from app import db

class Car(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    brand = db.Column(db.String(255))
    # Марка
    model = db.Column(db.String(255))
    # Модель
    price = db.Column(db.Float(64))
    # Цена
    image_url = db.Column(db.String(255))
    # Ссылка на постер
    description = db.Column(db.String(1024))
    # Описание
    production_date = db.Column(db.Integer())
    # Год производства
    