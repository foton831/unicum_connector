import os
import time
import requests
from env_const import EnviromentVariables as ev

class Authentificator:
    LIFE_TERM = 60 * 30  # Срок действия токена (в секундах)

    @classmethod
    def get_token(cls):
        # Проверяем, нужно ли обновить токен или он еще действителен
        if time.time() - cls.get_refresh_time() >= cls.LIFE_TERM or os.environ.get('TOKEN') is None:
            cls.refresh()  # Если токен недействителен, обновляем его
        return os.environ.get('TOKEN')

    @classmethod
    def set_token(cls, token:str):        
        os.environ['TOKEN'] = token  # Устанавливаем новый токен в переменные окружения
        cls.set_refresh_date()  # Записываем время обновления токена

    @classmethod
    def refresh(cls):
        # Пытаемся обновить токен, отправляя запрос на сервер
        data = {
            'login': ev.get_login(),
            'password': ev.get_password()
        } 
        try:
            response = requests.post(f'{ev.get_url()}/wjson/iamrobot.json', json=data)
            if response.status_code == 200:
                token = response.json().get('token')
                if token:
                    cls.set_token(token)  # Устанавливаем новый токен, если получен успешный ответ
            else:
                print('Ошибка при обновлении токена:', response.text)
        except Exception as e:
            print('Ошибка при отправке запроса на обновление токена:', e)

    @classmethod
    def get_refresh_time(cls):
        refresh_time_str = os.environ.get('REFRESH_TIME')
        if refresh_time_str is not None:
            try:
                return float(refresh_time_str)  # Возвращаем время последнего обновления токена
            except ValueError:
                print('Ошибка: недопустимое значение REFRESH_TIME')
        return 0

    @classmethod
    def set_refresh_date(cls):
        os.environ['REFRESH_TIME'] = str(time.time())  # Записываем текущее время как время обновления токена
    