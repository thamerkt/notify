import pika
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from django.conf import settings
from .models import Notification
from django.db import transaction, connection
import threading
import time
from django.db import close_old_connections

# Config
RABBITMQ_HOST = getattr(settings, 'RABBITMQ_HOST', 'host.docker.internal')
RABBITMQ_PORT = getattr(settings, 'RABBITMQ_PORT', 5672)
RABBITMQ_QUEUE = getattr(settings, 'RABBITMQ_QUEUE', 'generate_contract')

SMTP_SERVER = 'smtp-relay.brevo.com'
SMTP_PORT = 587
SMTP_USERNAME = '7e8bcf002@smtp-brevo.com'
SMTP_PASSWORD = 'tGMsIDKfLYh0vbWS'
FROM_EMAIL = 'kthirithamer2@gmail.com'

def send_email(to_email, subject, body):
    msg = MIMEMultipart()
    msg['From'] = FROM_EMAIL
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
        print(f"✅ Email sent to {to_email}")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

def callback(ch, method, properties, body):
    print("📨 Received message:", body)
    try:
        # Ensure DB connection is valid (fixes long-lived thread issues)
        close_old_connections()

        message = json.loads(body)
        event = message.get('event')
        payload = message.get('payload', {})
        email = payload.get('email')
        user = payload.get('user')
        rental_request_id = payload.get('rental_request_id')
        status = payload.get('status')

        print(f"🔍 User: {user}")

        subject = ""
        body_text = ""

        if event == 'rental.confirmed':
            subject = "Votre réservation a été confirmée"
            body_text = f"Bonjour,\n\nVotre demande de location (ID: {rental_request_id}) a été confirmée. Statut : {status}.\n\nMerci."
        elif event == 'rental.canceled':
            subject = "Votre réservation a été annulée"
            body_text = f"Bonjour,\n\nVotre demande de location (ID: {rental_request_id}) a été annulée. Statut : {status}.\n\nMerci."
        else:
            print(f"⚠️ Unhandled event type: {event}")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        send_email(email, subject, body_text)

        # Save to database
        with transaction.atomic():
            notif = Notification(user=user, title=subject)
            notif.save()
            print(f"✅ Notification saved: {notif.id} - {notif.title}")

    except Exception as e:
        print(f"❌ Error processing message: {e}")
    finally:
        ch.basic_ack(delivery_tag=method.delivery_tag)


def start_notification_service():
    print("🚀 Notification service starting...")
    while True:
        try:
            amqp_url = 'amqps://poqribhv:LzwYFbmBXeyiQI0GveEEe-YQyDeH126c@kebnekaise.lmq.cloudamqp.com/poqribhv'
            parameters = pika.URLParameters(amqp_url)
            connection = pika.BlockingConnection(parameters)
            channel = connection.channel()
            channel.queue_declare(queue=RABBITMQ_QUEUE, durable=True)
            channel.basic_qos(prefetch_count=1)
            channel.basic_consume(queue=RABBITMQ_QUEUE, on_message_callback=callback)

            print("✅ Waiting for messages...")
            channel.start_consuming()

        except pika.exceptions.AMQPConnectionError as e:
            print(f"🐇 Connection failed: {e}. Retrying in 5 seconds...")
            time.sleep(5)
        except Exception as e:
            print(f"❌ Unexpected error: {e}. Retrying in 5 seconds...")
            time.sleep(5)
