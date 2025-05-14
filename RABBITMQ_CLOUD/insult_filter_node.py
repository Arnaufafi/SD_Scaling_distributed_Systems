import pika
import boto3
import json
import signal
import sys

# Configuración
QUEUE_NAME = 'text_queue'
RESULT_NAME = 'RESULTS'
LAMBDA_FUNCTION_NAME = 'InsultFilterLambda'
CENSOR_LIST = ['fool', 'insult', 'idiot', 'stupid', 'dumb']

# Conectar a RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
channel.queue_declare(queue=QUEUE_NAME, durable=False)
channel.basic_qos(prefetch_count=1)

# Cliente de AWS Lambda
lambda_client = boto3.client('lambda', region_name='us-east-1')  # Cambia la región si es necesario

print("Consumer is waiting for tasks...")

# Función para manejar el apagado amigable
def graceful_exit(signal, frame):
    print("Exiting gracefully...")
    channel.stop_consuming()  # Detiene el consumidor
    connection.close()  # Cierra la conexión a RabbitMQ
    sys.exit(0)  # Sale del programa

# Configurar el manejador para la señal SIGINT (Ctrl+C)
signal.signal(signal.SIGINT, graceful_exit)

def process_and_store(ch, method, properties, body):
    message = body.decode('utf-8')

    try:
        response = lambda_client.invoke(
            FunctionName=LAMBDA_FUNCTION_NAME,
            InvocationType='RequestResponse',
            Payload=json.dumps({
                'text': message,
                'censor_list': CENSOR_LIST
            })
        )

        result_payload = response['Payload'].read().decode('utf-8')
        result = json.loads(result_payload)['body']

        print(f"Consumed and censored: {result}")

    except Exception as e:
        print("Error invoking Lambda:", e)

    # Confirmar que el mensaje fue procesado
    ch.basic_ack(delivery_tag=method.delivery_tag)

# Configurar el consumidor
channel.basic_consume(queue=QUEUE_NAME, on_message_callback=process_and_store)

print("Waiting for messages. To exit, press CTRL+C")
channel.start_consuming()  # Inicia el proceso de consumo
