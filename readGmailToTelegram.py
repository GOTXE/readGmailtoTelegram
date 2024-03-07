'''
Script para recibir notificaciones de correos electrónicos según el  en Telegram

Funcionalidad:

    Este script utiliza la API de Gmail para buscar correos nuevos en la bandeja de entrada del usuario.
    Cuando encuentra un correo nuevo con un asunto específico, envía una notificación a un grupo de Telegram con el asunto y el cuerpo completo del mensaje.
    Los correos nuevos se marcan como leídos automáticamente después de enviar la notificación.

Requisitos:

    Se requieren credenciales de API de Gmail para autenticarse con el servicio.
    El token de autenticación se guarda en un archivo binario ('token.pickle') para evitar la necesidad de autenticarse repetidamente.
    El archivo de credenciales JSON ('credentials.json') debe proporcionarse previamente y contener los detalles de la aplicación de API registrada en la consola de desarrolladores de Google.
    Se necesita un token de bot de Telegram y el ID del chat donde se enviarán las notificaciones.

Instrucciones de uso:

    Asegúrate de tener los archivos 'credentials.json' y 'token.pickle' en el mismo directorio que este script.
    Configura un bot de Telegram y obtén el token del bot y el ID del chat donde quieres recibir las notificaciones.
    Completa el archivo de configuración 'config.ini' con el token del bot de Telegram y el ID del chat.
    Ejecuta este script utilizando Python 3.
    El script buscará correos nuevos cada minuto y enviará notificaciones a Telegram si encuentra un correo con el asunto especificado en el archivo de configuración.

Nota: Este script está diseñado para ejecutarse continuamente en segundo plano para monitorear los correos entrantes de forma automática y reenviarlos a un bot de telegram.

Autor: Gotxe
Versión: 1.4

Mejoras:
    - v1.4: Se añade el manejo de excepciones y errores, registrándolos en un archivo 
    - v1.3: Se amplia el texto que puede enviar dividido en varios mensajes.
    - v1.2: Se amplia el texto que puede enviar en 1 solo mensaje.
    
Correciones:
    - v1.1: Cortaba el texto del cuerpo del mensaje. 

'''
import os
import time
import base64
import pickle
import asyncio
import datetime
import traceback
import configparser
from aiogram import Bot
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow


# Constantes
# Constants
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
MAX_MESSAGE_LENGTH = 4000   # Asegúrate de que este valor sea menor de 4000
                            ## Not longer than 4000

# Leer la configuración desde el archivo config.ini
# Read configuration from config.ini archive
config = configparser.ConfigParser()
config.read('config.ini')

# Obtener los valores de configuración
# Gathers config values
TELEGRAM_TOKEN = config['Telegram']['token']
TELEGRAM_CHAT_ID = config['Telegram']['chat_id']
CREDENTIALS_FILE = config['Gmail']['credentials_file']
TOKEN_FILE = config['Gmail']['token_file']

async def buscar_correos_y_enviar_telegram(ultima_verificacion):
    creds = None
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)
    
    # Construir el servicio de Gmail
    # Builds Gmail service
    service = build('gmail', 'v1', credentials=creds)

    # Llamar a la API de Gmail para buscar correos nuevos desde la última verificación
    # Calls Gmail API to look for new mail since last verification
    try:
        results = service.users().messages().list(userId='me', q='is:unread subject:"PLACE YOUR SUBJECT"').execute() # Cambia tu asunto ## Change your subject here !!
    except Exception as e:
        # Manejar excepciones y guardarlas en el archivo de errores
        # Saving exceptions to error log
        log_file = os.path.join('logs', 'errores.log')
        with open(log_file, 'a') as f:
            f.write(f'{datetime.datetime.now()} - Error: {str(e)}\n')
            traceback.print_exc(file=f)
        return

    messages = results.get('messages', [])
    if messages:
        print(datetime.datetime.now(), ': MENSAJES NUEVOS !!:')
        bot = Bot(token=TELEGRAM_TOKEN)
        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id'], format='full').execute()
            subject = None
            headers = msg.get('payload', {}).get('headers', [])
            for header in headers:
                if header['name'] == 'Subject':
                    subject = header['value']
                    break
            body = obtener_cuerpo_mensaje(msg)
            subject_and_body = f'{subject}:\n{body}'
            if len(subject_and_body) <= MAX_MESSAGE_LENGTH:
                await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=subject_and_body)
            else:
                # Dividir el cuerpo del mensaje en partes si es demasiado largo
                # Divide body message if it is longer than 4000
                parts = [body[i:i+MAX_MESSAGE_LENGTH] for i in range(0, len(body), MAX_MESSAGE_LENGTH)]
                for i, part in enumerate(parts):
                    await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=f'{subject} (parte {i + 1}):\n{part}')
            service.users().messages().modify(userId='me', id=message['id'], body={'removeLabelIds': ['UNREAD']}).execute()
    else:
        print(datetime.datetime.now(),': No se encontraron mensajes nuevos desde la última verificación.')

# Función para obtener el cuerpo completo del mensaje
# Function to obtain message body
def obtener_cuerpo_mensaje(message):
    if 'parts' in message['payload']:
        parts = message['payload']['parts']
        body = ''
        for part in parts:
            if part['mimeType'] == 'text/plain':
                data = part['body']['data']
                data = data.replace('-', '+').replace('_', '/')
                decoded_data = base64.b64decode(data)
                body += decoded_data.decode('utf-8')
        return body
    elif 'data' in message['payload']['body']:
        data = message['payload']['body']['data']
        data = data.replace('-', '+').replace('_', '/')
        decoded_data = base64.b64decode(data)
        return decoded_data.decode('utf-8')

# Función principal
# Principal function 
def main():
    # Definir la última vez que se verificaron los correos (inicialmente, la hora actual menos 1 minuto)
    # Defines last time email verification (initially, actual time minus 1 minute)
    ultima_verificacion = datetime.datetime.now() - datetime.timedelta(minutes=1)
    
    # Loop infinito para buscar correos continuamente
    # Infinite loop looking for emails
    while True:
        asyncio.run(buscar_correos_y_enviar_telegram(ultima_verificacion))
        # Esperar 1 minuto antes de realizar la próxima búsqueda
        # Waiting 1 minute before next check
        time.sleep(60)
        # Actualizar el tiempo de la última verificación a la hora actual
        # Updates last time verification to actual time
        ultima_verificacion = datetime.datetime.now()

if __name__ == '__main__':
    main()
