import os
import uuid
import requests
import urllib3
from flask import Flask, request, jsonify
from flask_cors import CORS

# отключаем предупреждения: это нужно для корректной работы с сертификатами минцифры
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)
# разрешаем перекрестные запросы: это позволит вашему index.html обращаться к этому серверу
CORS(app)

@app.route('/auth', methods=['POST'])
def get_token():
    auth_key = request.json.get('auth_key')
    if not auth_key:
        return jsonify(dict(error="отсутствует ключ авторизации")), 400

    url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
    payload = {'scope': 'GIGACHAT_API_PERS'}
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json',
        'RqUID': str(uuid.uuid4()),
        'Authorization': f'Basic {auth_key}'
    }
    
    try:
        # отключаем проверку сертификатов: используем параметр verify=False
        response = requests.post(url, headers=headers, data=payload, verify=False)
        return jsonify(response.json())
    except Exception as e:
        return jsonify(dict(error=str(e))), 500

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    token = data.get('token')
    messages = data.get('messages')
    
    if not token or not messages:
        return jsonify(dict(error="некорректные данные запроса")), 400
    
    url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    payload = {
        "model": "GigaChat",
        "messages": messages,
        "stream": False
    }
    
    try:
        # выполняем запрос к апи: без проверки ssl-сертификатов
        response = requests.post(url, headers=headers, json=payload, verify=False)
        return jsonify(response.json())
    except Exception as e:
        return jsonify(dict(error=str(e))), 500

if __name__ == '__main__':
    # конфигурация порта: обязательна для деплоя на render
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
