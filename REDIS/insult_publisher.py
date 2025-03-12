import pika

# Connect to RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

channel.queue_declare(queue='insult')

# Define the callback function
def callback(ch, method, properties, body):
    message = body.decode()
    channel.exchange_declare(exchange='insult', exchange_type='fanout')
    channel.basic_publish(exchange='insult', routing_key='', body=message)
    print(f" [x] Sent '{message}'")

# Consume messages
channel.basic_consume(queue='insult', on_message_callback=callback, auto_ack=True)

channel.start_consuming()