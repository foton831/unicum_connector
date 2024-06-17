import os
import time
import requests
import sqlite3
import logging
from env_const import EnviromentVariables as ev


class Authentificator:
    LIFE_TERM = 60 * 30  # Срок действия токена (в секундах)

    @classmethod
    def get_token(cls):
        # Проверяем, нужно ли обновить токен или он еще действителен
        if os.environ.get('TOKEN') is None or time.time() - cls.get_refresh_time() >= cls.LIFE_TERM:
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
                logging.error('Ошибка при обновлении токена:', response.text)
        except requests.RequestException as e:
            logging.error('Ошибка при отправке запроса на обновление токена:', e)

    @classmethod
    def get_refresh_time(cls):
        refresh_time_str = os.environ.get('REFRESH_TIME')
        if refresh_time_str is not None:
            try:
                return float(refresh_time_str)  # Возвращаем время последнего обновления токена
            except ValueError:
                logging.error('Ошибка: недопустимое значение REFRESH_TIME')
        return 0

    @classmethod
    def set_refresh_date(cls):
        os.environ['REFRESH_TIME'] = str(time.time())  # Записываем текущее время как время обновления токена

class UnicumDB:
    @classmethod
    def create_tables(cls):
        cls.create_curstate()
    
    @classmethod
    def create_curstate(cls):
        conn = None
        try:
            conn = sqlite3.connect('unicum.db')
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE IF NOT EXISTS curstate_queue (unicum_guid VARCHAR(36))")
            conn.commit()
            cursor.execute("""CREATE TABLE IF NOT EXISTS curstate (
                                guid VARCHAR(36),
                                state TEXT,
                                vendscount INTEGER,
                                vendscost INTEGER,
                                empty_cells INTEGER,
                                update_datetime DATETIME
                            )""")
            conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Ошибка при создании таблиц: {e}")
        finally:
            if conn:
                conn.close()
