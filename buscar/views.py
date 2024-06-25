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


def getVacas(request):
    isGood, data = check_request(request, ['GET'], False)
    if not isGood:
        return data
    else:
        vacas_ = list(vacas.find({}, {'_id':0}))
        return HttpResponse([{'vacas':vacas_}], content_type='application/json', status=200)
    
def getPartos(request):
    isGood, data = check_request(request, ['GET'], False)
    if not isGood:
        return data
    else:
        partos_ = list(partos.find({}, {'_id':0}))
        return HttpResponse([{'partos':partos_}], content_type='application/json', status=200)