from django.http import HttpResponse
from django.conf import settings
from datetime import datetime, timedelta

import pymongo
import sys
sys.path.append('../')
from helpers.middleware import check_request
# Create your views here.

client = pymongo.MongoClient(settings.CONNECTION_STRING)
db = client[settings.DB_NAME]
vacas = db['vacas']
partos = db['partos']


def compra(request):
    keys_info={
        'ariete': (str), 'categoria': (str),
        'peso': (int, float), 'rancho': (str),
        'lote': (str), 'raza': (str)}
    isGood, data = check_request(request, ['POST'], True, keys_info=keys_info)

    if not isGood:
        # this is going to be a HTTP Response object
        return data
    else:
         # check if ariete exists
        ariete = data['ariete']
        vaca = vacas.find_one({'ariete':ariete}, {'ariete': 1, '_id': 0})
        if not vaca:
            res = vacas.insert_one(data)
            if res.inserted_id:
                return HttpResponse([{'message':'Se agrego con exito la compra'}], content_type='application/json', status=200)
            else:
                return HttpResponse([{'message':'Se produjo un error al agregar la compra'}], content_type='application/json', status=500)
        else: 
            return HttpResponse([{'message':'Ya existe el ariete'}], content_type='application/json', status=400)
        

def empadre(request):
    keys_info = {'ariete': (str), 'fecha': (datetime)}
    isGood, data = check_request(request, 'PUT', True, keys_info=keys_info)
    days_to_add = 283
    
    if isGood:
        ariete = data['ariete']
        # check if ariete exits
        res = vacas.find_one({'ariete': ariete}, {'prenada':1, '_id':0})
        if res == None:
            return HttpResponse([{'message':'No existe el ariete'}], content_type='application/json', status=404)
        else:
            if ('prenada' in res and not res['prenada']) or 'prenada' not in res:
                result = vacas.update_one({'ariete': ariete},{'$set': {'prenada': True}})
                
                if result.matched_count == 0:
                    return HttpResponse([{'message':'La vaca con ariete {} no se encontro'.format(ariete)}], content_type='application/json', status=404)
                elif result.modified_count == 1:
                    print('entre')
                    programado = datetime.combine(data['fecha'] + timedelta(days=days_to_add), datetime.min.time())
                    data['fecha'] = datetime.combine(data['fecha'], datetime.min.time())
                    data.update({'metodo':'inseminacion', 'fecha_programada': programado})

                    res = partos.insert_one(data)
                    if res.inserted_id:
                        return HttpResponse([{'message':'Se agrego la inseminacion a la vaca {} con exito'.format(ariete)}], content_type='application/json', status=200)
                    else:
                        vacas.update_one({'ariete': ariete},{'$set': {'prenada': False}})
                        return HttpResponse([{'message':'Hubo un error al guardar el empadre'.format(ariete)}], content_type='application/json', status=500)
                else:
                    return HttpResponse([{'message':'Se produjo un error al agregar la inseminacion '}], content_type='application/json', status=500)
            else:
                return HttpResponse([{'message':'La vaca ya se encuentra gestando'}], content_type='application/json', status=400)

    else:
        return data
