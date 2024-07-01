from django.http import HttpResponse

def checar_embarazo(data, ariete, partosTable, vacasTable):

    res = partosTable.insert_one(data)
    if res.inserted_id:
        return HttpResponse([{'message':'Se agrego la inseminacion a la vaca {} con exito'.format(ariete)}], content_type='application/json', status=200)
    else:
        vacasTable.update_one({'ariete': ariete},{'$set': {'prenada': False}})
        return HttpResponse([{'message':'Hubo un error al guardar el empadre'.format(ariete)}], content_type='application/json', status=500)