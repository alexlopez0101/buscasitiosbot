import telebot
import openpyxl
import os
from dotenv import load_dotenv
import requests
from io import BytesIO

# Cargar variables de entorno
load_dotenv()

# Configurar el bot
BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError("No se encontró el token del bot. Asegúrate de tener un archivo .env con BOT_TOKEN=tu_token")

bot = telebot.TeleBot(BOT_TOKEN)

# Cargar el archivo Excel desde OneDrive
EXCEL_URL = os.getenv('EXCEL_URL')
if not EXCEL_URL:
    raise ValueError("No se encontró la URL del Excel. Asegúrate de tener un archivo .env con EXCEL_URL=tu_url")

try:
    response = requests.get(EXCEL_URL)
    response.raise_for_status()  # Esto lanzará una excepción para códigos de estado HTTP no exitosos
    workbook = openpyxl.load_workbook(BytesIO(response.content), data_only=True)
    print("Archivo Excel cargado exitosamente desde OneDrive")
except requests.RequestException as e:
    print(f"Error al descargar el archivo Excel: {e}")
    exit(1)
except Exception as e:
    print(f"Error al cargar el archivo Excel: {e}")
    exit(1)

def crear_enlace_maps(latitud, longitud):
    return f"https://www.google.com/maps/search/?api=1&query={latitud},{longitud}"

def buscar_por_id(id):
    print(f"Buscando ID: {id}")
    sheet = workbook['Sitios Bogota']
    for row in sheet.iter_rows(min_row=2, values_only=True):
        if str(row[1]) == id:
            print(f"ID encontrado: {id}")
            latitud, longitud = row[18], row[19]
            maps_link = crear_enlace_maps(latitud, longitud)
            return (f"ID: {row[1]}\nNombre: {row[2]}\nDirección: {row[3]}\n"
                    f"Pto 0/1/0: {row[4]}\nPto 0/2/0: {row[5]}\nOperacion: {row[9]}\nLlaves en: {row[6]}\n"
                    f"Coordenadas: {latitud}, {longitud}\n"
                    f"Ubicación en Maps: {maps_link}")
    print(f"ID no encontrado: {id}")
    return "No se encontró el ID especificado."

def buscar_por_nombre(nombre):
    print(f"Buscando nombre: {nombre}")
    sheet = workbook['Sitios Bogota']
    for row in sheet.iter_rows(min_row=2, values_only=True):
        if row[2].lower() == nombre.lower():
            print(f"Nombre encontrado: {nombre}")
            latitud, longitud = row[18], row[19]
            maps_link = crear_enlace_maps(latitud, longitud)
            return (f"ID: {row[1]}\nNombre: {row[2]}\nDirección: {row[3]}\n"
                    f"Barrio: {row[4]}\nLocalidad: {row[5]}\n"
                    f"Coordenadas: {latitud}, {longitud}\n"
                    f"Ubicación en Maps: {maps_link}")
    print(f"Nombre no encontrado: {nombre}")
    return "No se encontró el nombre especificado."

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    print(f"Comando recibido: {message.text}")
    bot.reply_to(message, "Bienvenido! Usa /buscar_id [ID] o /buscar_nombre [Nombre] para buscar información.")

@bot.message_handler(commands=['buscar_id'])
def handle_buscar_id(message):
    print(f"Comando recibido: {message.text}")
    try:
        id = message.text.split()[1]
        resultado = buscar_por_id(id)
        bot.reply_to(message, resultado)
    except IndexError:
        print("Error: No se proporcionó ID")
        bot.reply_to(message, "Por favor, proporciona un ID después del comando. Ejemplo: /buscar_id 12345")

@bot.message_handler(commands=['buscar_nombre'])
def handle_buscar_nombre(message):
    print(f"Comando recibido: {message.text}")
    try:
        nombre = ' '.join(message.text.split()[1:])
        resultado = buscar_por_nombre(nombre)
        bot.reply_to(message, resultado)
    except IndexError:
        print("Error: No se proporcionó nombre")
        bot.reply_to(message, "Por favor, proporciona un nombre después del comando. Ejemplo: /buscar_nombre Parque Simón Bolívar")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    print(f"Mensaje recibido: {message.text}")
    bot.reply_to(message, "No entiendo ese comando. Por favor, usa /start para ver las instrucciones.")

# Iniciar el bot
if __name__ == "__main__":
    print("Bot iniciado. Presiona Ctrl+C para detener.")
    bot.polling()