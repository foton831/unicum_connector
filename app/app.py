from flask import Flask, request, jsonify
from datetime import datetime
import time
# from apscheduler.schedulers.background import BackgroundScheduler
from env_const import EnviromentVariables as ev
from models import Authentificator as auth
from curstate import curstate_task, select_all_curstate

import multiprocessing as mp

app = Flask(__name__)

# scheduler = BackgroundScheduler()
# # Запуск расписания задач перед обработкой запросов
# @app.before_request 
# def start_scheduler():    
#     if not scheduler.running:
#         scheduler.add_job(auth.get_token, 'interval', minutes=20)
#         scheduler.add_job(curstate_task, 'interval', minutes=ev.get_curstate_update_interval())        
#         scheduler.start()

# Метод для проверки работоспособности сервера
@app.route("/health", methods=['GET'])
def health():
    return jsonify(status='UP')

# Метод для получения токена аутентификации
@app.route('/get_token', methods=['POST'])
def get_token():
    try:
        return jsonify({'token': auth.get_token(), 'refresh_time': datetime.fromtimestamp(auth.get_refresh_time()) })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
# Метод для получения текущего состояния аппараторв
@app.route('/curstate_monitor', methods=['POST'])
def curstate_monitor():
    return jsonify({"machines":select_all_curstate()})

def curstate_scheduler():    
    while True:
      curstate_task()
      time.sleep(ev.get_curstate_update_interval())      

#Запуск сервера
if __name__ == '__main__':
    p = mp.Process(target=curstate_scheduler) 
    p.start()
    app.run(host='0.0.0.0', port=5000, debug=False)