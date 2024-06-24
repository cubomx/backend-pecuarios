from django.http import HttpResponse
import json

def check_request(request, methods, itJSON, get_values=[], keys_info={}):
    if not request.content_type == 'application/json':
        return (False, HttpResponse([[{'message':'No se envio el JSON'}]], content_type='application/json', status=400))
    if request.method not in methods:
        return (False, HttpResponse([[{'message':'Metodo {} no autorizado para este endpoint'.format(request.method)}]], content_type='application/json', status=400))
    # Check if all required parameters are present
    if len(get_values) > 0:
        missing_params = [param for param in get_values if param not in request.GET]
        if missing_params:
            # Store the missing parameters in a variable
            missing_params_str = ", ".join(missing_params)
            return (False, HttpResponse([[{'message':f'Faltan parametros: {missing_params_str}'}]], content_type='application/json', status=400))
    if itJSON:
            try:
                data = json.loads(request.body)
                # Check for missing obligatory keys
                missing_obligatory_keys = [key for key in keys_info if key not in data]
                
                if missing_obligatory_keys:
                    missing_keys_str = ", ".join(missing_obligatory_keys)
                    return (False, HttpResponse([[{'message':f'Faltan parametros obligatorios: {missing_keys_str}'}]], content_type='application/json', status=400))
                
                # Check for correct types
                incorrect_type_keys = [key for key, types in keys_info.items() if key in data and not isinstance(data[key], types)]
                
                if incorrect_type_keys:
                    incorrect_types_str = ", ".join(
                        f"{key} (esperado {types.__name__})"
                        if not isinstance(types, tuple)
                        else f"{key} (esperados {' o '.join(t.__name__ for t in types if isinstance(t, type))})"
                        for key, types in keys_info.items() if key in incorrect_type_keys
                    )

                    return (False, HttpResponse([[{'message':f'Tipo parametros obligatorios incorrectos: {incorrect_types_str}'}]], content_type='application/json', status=400))
                
                # Extract obligatory and optional keys
                extracted_data = {key: data[key] for key in keys_info if key in data}
                
                
                # Your processing logic here
                return (True, extracted_data)
            except json.JSONDecodeError:
                return (False, HttpResponse([[{'message':f'JSON incorrecto: {missing_params_str}'}]], content_type='application/json', status=400))
    return (True, None)