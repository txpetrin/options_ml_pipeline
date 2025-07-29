from flask import Flask, request, jsonify
import pika
import uuid
import json
import time

from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow all origins (simple for dev)

def connect_rabbitmq():
    for _ in range(10):
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
            return connection
        except pika.exceptions.AMQPConnectionError:
            time.sleep(2)
    return None

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    stock = data['stock']

    connection = connect_rabbitmq()
    channel = connection.channel()
    channel.queue_declare(queue='stock')

    # Create a temporary callback queue
    result = channel.queue_declare(queue='', exclusive=True)
    callback_queue = result.method.queue

    # Generate unique correlation ID
    corr_id = str(uuid.uuid4())
    response = None

    # Define callback function for result
    def on_response(ch, method, props, body):
        nonlocal response
        if props.correlation_id == corr_id:
            response = json.loads(body)

    # Subscribe to callback queue
    channel.basic_consume(queue=callback_queue, on_message_callback=on_response, auto_ack=True)

    # Publish request with reply_to and correlation_id
    channel.basic_publish(
        exchange='',
        routing_key='stock',
        properties=pika.BasicProperties(
            reply_to=callback_queue,
            correlation_id=corr_id
        ),
        body=json.dumps({'stock': stock})
    )

    # Wait for response (poll-based)
    while response is None:
        connection.process_data_events()
        
    print(f"Stock Histories : {response['stock_history']}", flush=True)
    print(f"Forecast : {response['forecast']}", flush=True)

    print(f"{type(response['forecast'])}", flush=True)


    return jsonify(response)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000)
