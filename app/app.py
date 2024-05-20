from flask import Flask, request, jsonify
import os
import threading
from models import Authentificator as auth
from curstate import thread_curstate

app = Flask(__name__)

# Запуск потоков перед обработкой запросов
@app.before_request 
def start_threads():
    # Проверяем наличие токена
    if os.environ.get('TOKEN') is None:
        auth.refresh()
    # Проверяем статус CURSTATE и запускаем поток обновления состояния
    if os.environ.get('CURSTATE') is None or os.environ.get('CURSTATE') == '0':
        os.environ['CURSTATE'] = '1'
        thread = threading.Thread(target=thread_curstate)
        thread.start()

# Метод для проверки работоспособности сервера
@app.route("/health", methods=['GET'])
def health():
    return jsonify(status='UP')

# Метод для получения токена аутентификации
@app.route('/get_token', methods=['GET'])
def get_token():
    try:
        return jsonify({'token': auth.get_token()})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Запуск сервера
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
