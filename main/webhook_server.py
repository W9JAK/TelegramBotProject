from flask import Flask, request, jsonify
from main import bot
from config import GROUP_CHAT_ID
import logging

app = Flask(__name__)


@app.route('/webhook/yookassa', methods=['POST'])
def yookassa_webhook():
    data = request.json
    if data.get('event') == 'payment.succeeded':
        amount = data['object']['amount']['value']
        description = data['object']['description']
        message = f"Платеж успешно проведен: {description} на сумму {amount} руб."
        bot.send_message(GROUP_CHAT_ID, message)
        return jsonify({'status': 'success'})
    else:
        return jsonify({'status': 'ignored'})

@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({'status': 'OK'})


if __name__ == '__main__':
    logging.basicConfig(filename='app.log', level=logging.DEBUG)
    app.run()
