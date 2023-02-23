import pika, sys, os, json
from transformers import pipeline
from dotenv import load_dotenv
from datetime import datetime
from trycourier import Courier
load_dotenv()

def main():
    # credentials = pika.PlainCredentials(os.getenv('RABBIT_USER'), os.getenv('RABBIT_PASSWORD'))
    credentials = pika.PlainCredentials('guest', 'guest')
    # connection = pika.BlockingConnection(pika.ConnectionParameters('localhost',5672,'/',credentials))
    connection = pika.BlockingConnection(pika.ConnectionParameters('some-rabbit',5672,'/',credentials))
    channel = connection.channel()

    # handle speech recognition
    def sendNotif(userEmail, transcription):
        client = Courier(auth_token=os.getenv('COURIER_AUTH_TOKEN'))
        resp = client.send_message(
            message={
                "to": {
                    "email": userEmail
                },
                "template": os.getenv('COURIER_TEMPLATE_ID'),
                "data": {
                    "transcription": transcription
                }
            }
        )
        print(resp)
    def transcribe(filePath):
        try:
            whisper = pipeline('automatic-speech-recognition', model='openai/whisper-base', chunk_length_s=60)
            return whisper(filePath)
        except Exception as e:
            print(e)
            return None

    def callback(ch, method, properties, body):
       print(" [x] Received %r" % body.decode())
       data = json.loads(body.decode())
       try:
           transcription = f'{transcribe(data["url"])["text"]}'
           if transcription is not None:
            sendNotif(data["userEmail"], transcription)
       except Exception as e:
           print(e)
           pass

    channel.basic_consume(queue='tasks', on_message_callback=callback, auto_ack=True)
    channel.start_consuming()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
