import requests
import time
from app import app, db, models

url = 'https://auto.ru/-/ajax/desktop/listing/'

headers = {
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'Connection': 'keep-alive',
    'Content-Length': '132',
    'content-type': 'application/json',
    'Cookie': '_csrf_token=0f7e6a1cb4de712580855ffab6e23cd65eab08c204910054; autoru_sid=a%3Ag5f7f444a207uqes3euboectllc43pt0.eb781edf11eb4010f18710ceeaa26aa3%7C1602176074755.604800.sDKrTHErNkm9NiE_DbNuvQ.yj_CbsRvDLnVQ6hMb1dri0DLvA1FRsWKpdEuvj4FzE8; autoruuid=g5f7f444a207uqes3euboectllc43pt0.eb781edf11eb4010f18710ceeaa26aa3; suid=95b8c63453c75e2a885968b0fe226282.1c365bc6e454a57e8bd6eb8032bf76ab; from=direct; yuidcs=1; X-Vertis-DC=myt; crookie=ovGkgULNidhV8wLj32I33L3ejL93oyVkA+uSnm4ye0gIS+XD1MJDWwedgiWUFSMGXaTiCLnAJNuDgzCsZ3WI0Knkx6k=; cmtchd=MTYwMjE3NjAxMjQ1NQ==; _ym_uid=15923217431034055406; _ym_visorc_22753222=b; _ym_isad=1; bltsr=1; yuidlt=1; yandexuid=4265084071587720280; my=YwA%3D; gdpr=0; from_lifetime=1602176239621; _ym_d=1602176241; _ym_uid=15923217431034055406; _ym_d=1602177700',
    'Host': 'auto.ru',
    'Origin': 'https://auto.ru',
    'Referer': '',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'same-origin',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36',
    'x-client-app-version': '202010.08.125206',
    'x-client-date': '1602176186983',
    'x-csrf-token': '0f7e6a1cb4de712580855ffab6e23cd65eab08c204910054',
    'x-page-request-id': '39cd0ae5071b6176d10a084bef94b201',
    'x-requested-with': 'fetch'
}

payload = {"category": "cars", "section": "all", "page": 0,"geo_radius": 200, "geo_id":[213]}

brands = [['HYUNDAI', 'SOLARIS'], ['KIA', 'RIO'], ['volkswagen', 'polo'], ['volkswagen', 'tiguan'], ['skoda', 'octavia']]

for brand in brands:
    page = 1

    while True:
        page += 1

        payload['page'] = page
        payload['catalog_filter'] = [{"mark": brand[0].upper(),"model": brand[1].upper()}]
        headers['Referer'] = 'https://auto.ru/moskva/cars/{}/{}/all/?output_type=list&page={}'.format(brand[0].upper(), brand[1].upper(), page)

        try:
            response = requests.post(url, headers = headers, json = payload).json()
            offers = response['offers']

            for offer in offers:
                if offer['section'] == 'new':

                    description = offer['description']
                    price = offer['price_info']['price']

                    model = offer['vehicle_info']['model_info']['name']
                    image_url = None
                    production_date = offer['documents']['year']

                    if len(offer['state']['image_urls']) > 0:
                        image_url = 'https:' + offer['state']['image_urls'][0]['sizes']['1200x900n']

                    
                    #print(description)
                    print(image_url)
                    print(price)
                    print(model)
                    print(production_date)

                    new_car = models.Car(brand = brand[0], model = brand[1], price = price, production_date = production_date, image_url = image_url, description = description)
                    db.session.add(new_car)
                    db.session.commit()
                else:
                    print('used')

                
                
            time.sleep(5)
        except Exception as e:
            print('PAGE', page)
            print(e)
            break

    print(page)
    


