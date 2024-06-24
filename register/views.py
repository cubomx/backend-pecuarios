from django.http import HttpResponse
from django.shortcuts import render
from django.conf import settings
import pymongo
import sys
sys.path.append('../')
from helpers.middleware import check_request
# Create your views here.

client = pymongo.MongoClient(settings.CONNECTION_STRING)
db = client[settings.DB_NAME]
vacas = db['vacas']


def compra(request):
    keys_info={
        'ariete': (str),
        'categoria': (str),
        'peso': (int, float),
        'rancho': (str),
        'lote': (str),
        'raza': (str)

    }
    isGood, data = check_request(request, ['POST'], True, keys_info=keys_info)

    if not isGood:
        # this is going to be a HTTP Response object
        return data
    else:
         # check if ariete exists
        ariete = data['ariete']
        vaca = vacas.find_one({'ariete':ariete}, {'ariete': 1})
        if not vaca:
            res = vacas.insert_one(data)
            if res.inserted_id:
                return HttpResponse([[{'message':'Se agrego con exito la compra'}]], content_type='application/json', status=200)
            else:
                return HttpResponse([[{'message':'Se produjo un error al agregar la compra'}]], content_type='application/json', status=500)
        else: 
            return HttpResponse([[{'message':'Ya existe el ariete'}]], content_type='application/json', status=400)