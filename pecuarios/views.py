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
ranchosTable = db['ranchos']

def addRancho(request):
    isGood, data = check_request(request, ['POST'], True, keys_info={'rancho': (str)})
    if isGood:
        # check if it already exists
        res = ranchosTable.find_one(data, {'rancho':1, '_id':0})
        if res:
            return HttpResponse([{'message':'Ya existe el rancho'}], content_type='application/json', status=400)
        else:
            data['lotes'] = []
            res_ins = ranchosTable.insert_one(data)
            if res_ins.inserted_id:
                return HttpResponse([{'message':'Se agrego con exito el rancho {}'.format(data['rancho'])}], content_type='application/json', status=200)
            else:
                return HttpResponse([{'message':'Se produjo un error al agregar el rancho'}], content_type='application/json', status=500)
    else:
        return data
    
def addLote(request):
    isGood, data = check_request(request, ['PUT'], True, keys_info={'lote': (str), 'rancho':(str)})
    if isGood:
        rancho = data['rancho']
        # check if it already exists
        res = ranchosTable.find_one({'rancho':rancho}, {'rancho':1, 'lotes': 1, '_id':0})
        if not res:
            return HttpResponse([{'message':'No existe el rancho'}], content_type='application/json', status=404)
        else:
            lote = data['lote']
            if lote in res['lotes']:
                return HttpResponse([{'message':'El lote {} ya existe'.format(lote)}], content_type='application/json', status=400)
            else:
                result = ranchosTable.update_one({'rancho': rancho},{'$push': {'lotes': lote}})
                if result.matched_count == 0:
                    return HttpResponse([{'message':'El rancho {} no se encontro'.format(rancho)}], content_type='application/json', status=404)
                if result.modified_count == 1:
                    return HttpResponse([{'message':'El lote {} se agrego al racnho {} con exito'.format(lote, rancho)}], content_type='application/json', status=404)
                else:
                    return HttpResponse([{'message':'Se produjo un error al agregar el nuevo lote {}'.format(lote)}], content_type='application/json', status=500)
                
def getRanchos(request):
    isGood, data = check_request(request, ['GET'], False)
    if not isGood:
        return data
    else:
        cursor = list(ranchosTable.find({},{'rancho':1, '_id':0}))
        ranchos = []
        for document in cursor:
            if 'rancho' in document:
                ranchos.append(document['rancho'])
        return HttpResponse([{'ranchos':ranchos}], content_type='application/json', status=200)
    
def getLotes(request):
    isGood, data = check_request(request, ['GET'], False, get_values=['rancho'])
    if not isGood:
        return data
    else:
        lotes = ranchosTable.find_one(data,{'lotes':1, '_id':0})
    if lotes: 
        return HttpResponse([lotes], content_type='application/json', status=200)
    return HttpResponse([{"lotes":[]}], content_type='application/json', status=200)