from flask import Flask, request, jsonify
import logging
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from models import Authentificator as auth
from curstate import curstate_task, select_all_curstate, select_all_tubes

app = Flask(__name__)

scheduler = BackgroundScheduler()

def start_scheduler():
    curstate_task()
    scheduler.add_job(curstate_task, 'cron', minute='*/2')
    scheduler.add_job(curstate_task, 'cron', hour='*/2')     
    scheduler.start()

def restart_scheduler ():
    global scheduler
    try: 
        print('Попытка выключить')
        scheduler.shutdown(wait=False)
        scheduler = BackgroundScheduler()
        start_scheduler()
    except Exception as e:
        print('Не удалось')

# Запуск расписания задач перед обработкой запросов
@app.before_request 
def before_request():
    if not scheduler.running:
        start_scheduler()

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

# Метод для получения текущего состояния аппараторв
@app.route('/tubes_monitor', methods=['POST'])
def tubes_monitor():
    return jsonify({"machines":select_all_tubes()})


# Метод для получения текущего состояния аппараторв
@app.route('/curstate_update', methods=['POST'])
def curstate_update():
    curstate_task()
    return jsonify({"status":"complete"})

#Запуск сервера
if __name__ == '__main__':
    start_scheduler()
    app.run(host='0.0.0.0', port=5000, debug=False)