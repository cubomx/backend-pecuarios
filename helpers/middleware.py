from django.http import HttpResponse
import json
from datetime import datetime, time
import pytz

def is_datetime(value):
    """
    Check if a value is of type datetime or can be converted to datetime.
    
    :param value: The value to check.
    :return: A tuple (is_valid, datetime_value). is_valid is a boolean indicating
             if the value is a valid datetime or convertible to one. datetime_value
             is the corresponding date object or None if not valid.
    """
    if isinstance(value, datetime):
        # Strip the time part
        return True, value.date()

    # Try parsing the value as a datetime string
    try:
        # Remove the Z if present and parse the datetime
        value = value.replace('Z', '+00:00')
        dt = datetime.fromisoformat(value).date()
        return True, dt
    except (ValueError, TypeError):
        pass

    # Additional formats can be added here if needed
    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
        "%m/%d/%Y",
        "%d/%m/%Y",
        "%m/%d/%Y %H:%M:%S",
        "%d/%m/%Y %H:%M:%S",
    ]

    for fmt in formats:
        try:
            dt = datetime.strptime(value, fmt).date()
            return True, dt
        except (ValueError, TypeError):
            continue

    return False, None

def check_request(request, methods, itJSON, get_values=[], keys_info={}):
    if itJSON and not request.content_type == 'application/json':
        return (False, HttpResponse([{'message':'No se envio el JSON'}], content_type='application/json', status=400))
    if request.method not in methods:
        return (False, HttpResponse([{'message':'Metodo {} no autorizado para este endpoint'.format(request.method)}], content_type='application/json', status=400))
    # Check if all required parameters are present
    if len(get_values) > 0:
        missing_params = [param for param in get_values if param not in request.GET]
        
        if missing_params:
            # Store the missing parameters in a variable
            missing_params_str = ", ".join(missing_params)
            return (False, HttpResponse([{'message':f'Faltan parametros: {missing_params_str}'}], content_type='application/json', status=400))
        else:
            params = {param: request.GET.get(param) for param in get_values}
            return (True, params)
    if itJSON:
            try:
                data = json.loads(request.body)
                # Check for missing obligatory keys
                missing_obligatory_keys = [key for key in keys_info if key not in data]
                
                if missing_obligatory_keys:
                    missing_keys_str = ", ".join(missing_obligatory_keys)
                    return (False, HttpResponse([{'message':f'Faltan parametros obligatorios: {missing_keys_str}'}], content_type='application/json', status=400))
                
                keys_date = {}
                clean_keys = {}
                # remove all datetime
                for key, types in keys_info.items():
                    clean_keys[key] = types
                    if not isinstance(types, (list, tuple)):
                        if types == datetime:
                            keys_date[key] = types
                            del clean_keys[key]
                    
                
                extracted_data = {}
                # Check for correct types
                incorrect_type_keys = [key for key, types in clean_keys.items() if key in data and not isinstance(data[key], types)]
                # check for dates
                for key, types in keys_date.items():
                    is_valid, event_date = is_datetime(data[key])
                    if is_valid:
                        extracted_data[key] = event_date
                    else:
                        incorrect_type_keys.append(key)
                
                if incorrect_type_keys:
                    incorrect_types_str = ", ".join(
                        f"{key} (esperado {types.__name__})"
                        if not isinstance(types, tuple)
                        else f"{key} (esperados {' o '.join(t.__name__ for t in types if isinstance(t, type))})"
                        for key, types in keys_info.items() if key in incorrect_type_keys
                    )

                    return (False, HttpResponse([{'message':f'Tipo parametros obligatorios incorrectos: {incorrect_types_str}'}], content_type='application/json', status=400))
                
                # Extract obligatory and optional keys
                extracted_data.update({key: data[key] for key in clean_keys if key in data})
                # Your processing logic here
                return (True, extracted_data)
            except json.JSONDecodeError:
                return (False, HttpResponse([{'message':f'JSON incorrecto: {missing_params_str}'}], content_type='application/json', status=400))
    return (True, None)

def get_today():
     # Define Mexico City time zone
    mx_tz = pytz.timezone('America/Mexico_City')

    # Get the current date and time in Mexico City time zone
    mx_now = datetime.now(mx_tz)
    
    # Replace the time to 00:00 hours
    mx_midnight = datetime.combine(mx_now.date(), time(0, 0), mx_tz)

    return mx_midnight