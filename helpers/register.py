from django.http import HttpResponse
from datetime import datetime, timedelta

def checar_embarazo(data, ariete, partosTable, vacasTable, vaca, diff_days):
    days_to_add = 283
    if ('prenada' in vaca and not vaca['prenada']) or 'prenada' not in vaca:
        result = vacasTable.update_one({'ariete': ariete},{'$set': {'prenada': True}})
        if result.matched_count == 0:
            return HttpResponse([{'message':'La vaca con ariete {} no se encontro'.format(ariete)}], content_type='application/json', status=404)
        elif result.modified_count == 1:
            programado = datetime.combine(data['fecha'] + timedelta(days=days_to_add-diff_days), datetime.min.time())
            data['fecha'] = datetime.combine(data['fecha'], datetime.min.time())
            data.update({'fecha_programada': programado})

            res = partosTable.insert_one(data)
            if res.inserted_id:
                return HttpResponse([{'message':'Se agrego la inseminacion a la vaca {} con exito'.format(ariete)}], content_type='application/json', status=200)
            else:
                vacasTable.update_one({'ariete': ariete},{'$set': {'prenada': False}})
                return HttpResponse([{'message':'Hubo un error al guardar el empadre'.format(ariete)}], content_type='application/json', status=500)
        else:
            return HttpResponse([{'message':'Se produjo un error al agregar la inseminacion '}], content_type='application/json', status=500)
    else:
        return HttpResponse([{'message':'La vaca {} ya se encuentra gestando'.format(ariete)}], content_type='application/json', status=400)

   
    
def checar_vaca(vacasTable, ariete, categorias, projection):
    

    vaca = vacasTable.find_one({'ariete':ariete}, projection)
    # checar si existe el ariete y si es de categoria vaca
    if not vaca or vaca == None:
        return HttpResponse([{'message':'El ariete {} no existe'.format(ariete)}], content_type='application/json', status=404)
    else:
        if  vaca['categoria'] not in categorias :
            return HttpResponse([{'message':'El ariete {} no es vaca'.format(ariete)}], content_type='application/json', status=400)
    return vaca