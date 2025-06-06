import json
import uuid
import base64
import pika
import os
from src.config import get_settings

def send_to_rabbitmq(image_bytes: bytes, filter_name: str) -> bytes:
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=get_settings().rabbitmq_host,
            port=get_settings().rabbitmq_port)
    )

    channel = connection.channel()
    # Объявляем временную очередь для ответа
    result = channel.queue_declare(queue='', exclusive=True)
    callback_queue = result.method.queue
    # Уникальный ID, чтобы сопоставить запрос и ответ
    corr_id = str(uuid.uuid4())
    # Кодируем изображение в base64
    encoded_image = base64.b64encode(image_bytes).decode()

    response = None

    # Колбэк, который будет вызываться при получении ответа
    def on_response(ch, method, props, body):
        nonlocal response
        if props.correlation_id == corr_id:
            response = json.loads(body.decode())["result"]
            ch.stop_consuming()

    channel.basic_consume(
        queue=callback_queue,
        on_message_callback=on_response,
        auto_ack=True
    )

    message = json.dumps({
        "photo": encoded_image,
        "filter": filter_name
    })

    # Отправка задачи с reply_to и correlation_id
    channel.basic_publish(
        exchange='',
        routing_key='task_queue',
        properties=pika.BasicProperties(
            reply_to=callback_queue,
            correlation_id=corr_id
        ),
        body=message.encode()
    )

    print(f"[x] Sent task with filter '{filter_name}', waiting for reply...")

    # Ожидаем ответ
    channel.start_consuming()

    # Декодируем base64 обратно в байты
    decoded_result = base64.b64decode(response)
    connection.close()
    return decoded_result
