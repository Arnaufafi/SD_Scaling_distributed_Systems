import pika
import time

# Connect to RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

# Declare a queue
channel.queue_declare(queue='insult')
print(" [*] To exit, press CTRL+C")
# Publish a message
while True:
    channel.basic_publish(exchange='', routing_key='insult', body='Bastard!')
    print(" [x] Sent 'Bastard to RabbitMQ!'")
    time.sleep(5)

