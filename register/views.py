from django.http import HttpResponse
from django.conf import settings
from datetime import datetime, timedelta

import pymongo
import sys
sys.path.append('../')
from helpers.middleware import check_request
from helpers.register import checar_embarazo
# Create your views here.

client = pymongo.MongoClient(settings.CONNECTION_STRING)
db = client[settings.DB_NAME]
vacasTable = db['vacas']
partosTable = db['partos']
nacimientos = db['nacimiento']
ranchosTable = db['ranchos']


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
        vaca = vacasTable.find_one({'ariete':ariete}, {'ariete': 1, '_id': 0})
        if not vaca:
            res = vacasTable.insert_one(data)
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
        vaca = vacasTable.find_one({'ariete': ariete}, {'prenada':1, '_id':0, 'categoria': 1})
        if vaca == None:
            return HttpResponse([{'message':'No existe el ariete'}], content_type='application/json', status=404)
        else:
            # checar que si sea una vaca, porque lo demas no podria gestar
            if vaca['categoria'] not in ['Vaca', 'Vaquilla'] :
                return HttpResponse([{'message':'El ariete {} no es vaca'}], content_type='application/json', status=400)

            elif ('prenada' in vaca and not vaca['prenada']) or 'prenada' not in vaca:
                result = vacasTable.update_one({'ariete': ariete},{'$set': {'prenada': True}})
                
                if result.matched_count == 0:
                    return HttpResponse([{'message':'La vaca con ariete {} no se encontro'.format(ariete)}], content_type='application/json', status=404)
                elif result.modified_count == 1:
                    programado = datetime.combine(data['fecha'] + timedelta(days=days_to_add), datetime.min.time())
                    data['fecha'] = datetime.combine(data['fecha'], datetime.min.time())
                    data.update({'metodo':'inseminacion', 'fecha_programada': programado})

                    return checar_embarazo(data, ariete, partosTable, vacasTable)
                else:
                    return HttpResponse([{'message':'Se produjo un error al agregar la inseminacion '}], content_type='application/json', status=500)
            else:
                return HttpResponse([{'message':'La vaca ya se encuentra gestando'}], content_type='application/json', status=400)

    else:
        return data

def nacimiento(request):
    keys_info = {'ariete': (str), 'rancho': (str), 'lote':(str), 'ariete': (str), 'ariete_madre': (str),
                 'fecha_nacimiento': (datetime), 'peso': (int, float), 'raza':(str), 'sexo':(str)}
    isGood, data = check_request(request, ['POST', 'PUT'], True, keys_info=keys_info)
    if isGood:
        # revisar si rancho existe
        rancho = data['rancho']
        exists = ranchosTable.find_one({'rancho':rancho}, {'_id':0, 'rancho':1})
        if exists:
            # revisar si vaca esta embarazada
            ariete_madre = data['ariete_madre']
            ariete_hijo = data['ariete']
            del data['ariete_madre']
            vaca = vacasTable.find_one({'ariete':ariete_madre}, {'_id':0, 'prenada':1}) 
            if vaca and ('prenada' in vaca and vaca['prenada']):
                ariete_en_uso = vacasTable.find_one({'ariete':ariete_hijo}, {'_id':1}) 
                if ariete_en_uso:
                    return HttpResponse([{'message':'Ariete hijo {} no se encuentra disponible'.format(ariete_madre)}], content_type='application/json', status=400)

                else:   
                    data['fecha_nacimiento'] = datetime.combine(data['fecha_nacimiento'], datetime.min.time())

                    # mover vaca de futuros partos a partos (nacimientos)
                    parto = partosTable.find_one({'ariete':ariete_madre}, {'_id':0, 'fecha':1})

                    if not parto:
                        # puede ser que hubo un error al agregar el nacimiento y cambiar la variable prenada
                        vacasTable.update_one({'ariete': ariete_madre},{'$set': {'prenada': False}})
                        return HttpResponse([{'message':'No se encontro parto en la vaca {}'.format(ariete_madre)}], content_type='application/json', status=404)
                    else:
                        partosTable.delete_one({'ariete':ariete_madre})
                        
                        sexo = data['sexo']
                        fecha_nacimiento = data['fecha_nacimiento']
                        dias_gestacion = fecha_nacimiento - parto['fecha']
                        # agregar a categoria
                        data['categoria'] = 'Becerro' if sexo == 'Macho' else 'Becerra'

                        del data['sexo']
                        nacimientos.insert_one({'fecha':fecha_nacimiento,'ariete':ariete_hijo, 'estado':'vivo', 'genero':sexo, 'dias_gestacion':dias_gestacion.days})
                        # cambiar que vaca ya no esta embarazada y agregarle la referencia al ariete del hijo
                        vacasTable.update_one({'ariete': ariete_madre},{'$set': {'prenada': False}, '$push': {'partos':ariete_hijo}})
                        
                        # anadir la nueva vaca como en compra pero ademas anadir los datos iniciales
                        data['etapa_1'] = {'peso_inicio': data['peso'], 'fecha_inicio':data['fecha_nacimiento']}
                        del data['fecha_nacimiento']
                        del data['peso']
                        res_vaca = vacasTable.insert_one(data)
                        if res_vaca.inserted_id:
                            return HttpResponse([{'message':'Se registro con exito el nacimiento del ariete hijo {} de la vaca {}'.format(ariete_hijo, ariete_madre)}], content_type='application/json', status=200)
                        else:
                            return HttpResponse([{'message':'Se produjo un error al agregar el hijo de la vaca {}'.format(ariete_madre)}], content_type='application/json', status=500)

            else:
                # quiere decir que si existe la vaca pero no esta embarazada
                if vaca:
                    return HttpResponse([{'message':'Vaca {} no se encuentra gestando'.format(ariete_madre)}], content_type='application/json', status=404)
                else:
                    return HttpResponse([{'message':'No se encontro vaca con el ariete {}'.format(ariete_madre)}], content_type='application/json', status=404)
        else:
            return HttpResponse([{'message':'Rancho no encontrado'}], content_type='application/json', status=404)
    else:
        return data
    
def palpaciones(request):
    keys_info = {'ariete': (str), 'dias': (int), 'fecha':(datetime)}
    isGood, data = check_request(request, ['POST'], True, keys_info=keys_info)
    days_to_add = 283

    if isGood:
        # checar si es 0 los dias, por lo tanto fue inseminacion artificial el metodo
        vaca = vacasTable.find_one({'ariete':data['ariete']}, {'_id':0, 'categoria':1})
        # checar si existe el ariete y si es de categoria vaca
        if not vaca or vaca == None:
            return HttpResponse([{'message':'El ariete {} no existe'}], content_type='application/json', status=404)
        else:
            if  vaca['categoria'] not in ['Vaca', 'Vaquilla'] :
                return HttpResponse([{'message':'El ariete {} no es vaca'}], content_type='application/json', status=400)
        dias = data['dias']
        if dias == 0:
            data['metodo'] = 'inseminacion artificial'
            data['fecha_programada'] = datetime.combine(data['fecha'] + timedelta(days=days_to_add), datetime.min.time())
        else:
            # restar los dias a la fecha actual (asi sabriamos cuando fue masomenos)
            data['metodo'] = 'inseminacion'
            data['fecha_programada'] = datetime.combine(data['fecha'] + timedelta(days=days_to_add-dias), datetime.min.time())

            return checar_embarazo(data, data['ariete'], partosTable, vacasTable)
        print(data)
    else:
        return data
    
def destete(request):
    keys_info = {'ariete':(str), 'fecha':(str), 'peso':(int, float)}
    isGood, data = check_request(request, ['PATCH'], True, keys_info=keys_info)

    if isGood:
        # checar que la vaca existe

        # revisar que no se haya destetado ya

        # cambiar de categoria y agregar los datos
        print(data)
        return HttpResponse([{'message':data}], content_type='application/json', status=200)
    
def mal_nacimiento(request):
    keys_info = {'ariete':(str), 'suceso':(str), 'fecha':(datetime)}
    isGood, data = check_request(request, ['PATCH'], True, keys_info=keys_info)

    if isGood:
        # checar que la vaca madre estaba esperando hijo (checar tabla partos futuros)

        # mover la cria fallecida a partos pero no al inventario y poner que la madre se encuentra no gestando
        return HttpResponse([{'message':data}], content_type='application/json', status=200)
    else:
        return data

# venta total/individual o muerte
def evento(request):
    keys_info={'tipo':(str), 'fecha':(datetime)}
    isGood, data = check_request(request, ['PUT', 'UPDATE'], True, keys_info=keys_info)

    if isGood:
        # checar el tipo para saber que otros datos buscar


        # if VENTA LOTE
            # obtener rancho, lote y peso
            # checar que rancho y lote exista
            # mover lote a vendidos y registar el peso/fecha
            # eliminar lote de la lista de lotes
        
        # if VENTA_INDIV
            # obtener ariete, peso
            # checar que vaca existe
            # mover a vendidas y registar el peso/fecha
        
        # if MUERTE_INDIV
            # obtener ariete
            # checar que vaca existe
            # mover a fallecidas y registar la fecha
        return HttpResponse([{'message':data}], content_type='application/json', status=200)
    else:
        return data
    
def semental(request):
    keys_info={'ariete':(str), 'peso': (int, float), 'fecha':(datetime)}
    isGood, data = check_request(request, ['PUT', 'UPDATE'], True, keys_info=keys_info)

    if isGood:
        # checar si vaca existe
        # guardar los datos y cambiar la etapa
        return HttpResponse([{'message':data}], content_type='application/json', status=200)
    else:
        return data
    