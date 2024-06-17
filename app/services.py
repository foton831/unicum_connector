import requests
import logging
from env_const import EnviromentVariables as ev
from models import Authentificator as auth

def getmachines():        
    """
    Функция для получения списка машин.

    Returns:
        dict or None: Результат запроса в формате словаря или None в случае ошибки.
    """
    data = {
        'auth_token': auth.get_token(),
        'subcompanies': True
    }
    try:
        response = requests.post(f'{ev.get_url()}/wjson/getmachines.json', json=data)
        if response.status_code == 200:            
            result = response.json()
            set_token_from_result(result=result)
            return result
        else:
            logging.error(f"Ошибка при выполнении запроса getmachines: {response.status_code}")
    except requests.RequestException as e:
        logging.error(f"Ошибка при выполнении запроса getmachines: {e}")
    return None

def curstate(guid):        
    """
    Функция для получения текущего состояния машины по её идентификатору.

    Args:
        guid (str): Идентификатор машины.

    Returns:
        dict or None: Результат запроса в формате словаря или None в случае ошибки.
    """
    data = {
        'auth_token': auth.get_token(),
        "machineguid": guid
    }
    try:
        response = requests.post(f'{ev.get_url()}/wjson/curstate.json', json=data)
        if response.status_code == 200:
            result = response.json()
            set_token_from_result(result=result)
            return result
        else:
            logging.error(f"Ошибка при выполнении запроса curstate : {response.status_code}, guid = {guid}")
    except requests.RequestException as e:
        logging.error(f"Ошибка при выполнении запроса curstate: {e}")
    return None

def set_token_from_result(result):
    """
    Функция для обновления токена аутентификации на основе результата запроса.

    Args:
        result (dict): Результат запроса в формате словаря.
    """
    try:
        token = result.get('user', {}).get('token')
        if token is not None:
            auth.set_token(token)
    except Exception as e:
        logging.error(f"Ошибка в set_token_from_result: {e}")
