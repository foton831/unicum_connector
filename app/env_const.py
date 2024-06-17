from dotenv import load_dotenv
import os

load_dotenv()

class EnviromentVariables:
    _URL = os.environ.get('URL')
    _LOGIN = os.environ.get('LOGIN')
    _PASSWORD = os.environ.get('PASSWORD')
    _CURSTATE_UPDATE_INTERVAL = os.environ.get('CURSTATE_UPDATE_INTERVAL', '60')

    @classmethod
    def get_url(cls):
        return cls._URL
    
    @classmethod
    def get_login(cls):
        return cls._LOGIN
    
    @classmethod
    def get_password(cls):
        return cls._PASSWORD   
    
    @classmethod
    def get_curstate_update_interval(cls):
        return float(cls._CURSTATE_UPDATE_INTERVAL)