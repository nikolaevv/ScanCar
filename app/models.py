from app import db

class Car(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    brand = db.Column(db.String(255))
    # Марка
    model = db.Column(db.String(255))
    # Модель
    price = db.Column(db.Float(64))
    # Цена
    #image_url = db.Column(db.String(255))
    # Ссылка на постер
    description = db.Column(db.String(9000))
    # Описание
    production_date = db.Column(db.Integer())
    # Год производства
    color = db.Column(db.String(255))
    # Цвет автомобиля
    bodywork = db.Column(db.String(255))
    # Кузов
    engine = db.Column(db.String(255))
    # Двигатель
    tax = db.Column(db.String(255))
    # Налог
    kpp = db.Column(db.String(255))
    # Коробка передач
    image_url_1 = db.Column(db.String(255))
    # Ссылка на постер 1
    image_url_2 = db.Column(db.String(255))
    # Ссылка на постер 1
    image_url_3 = db.Column(db.String(255))
    # Ссылка на постер 1
    steering_wheel = db.Column(db.String(255))
    # Руль
    customs = db.Column(db.String(255))
    # Растаможен ли