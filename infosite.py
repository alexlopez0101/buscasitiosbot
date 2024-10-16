import telebot
import os
from dotenv import load_dotenv
from telebot import types
import requests
import pandas as pd
from io import BytesIO

# Cargar variables de entorno
load_dotenv()

# URL de descarga directa del archivo en Google Drive
file_id = '1Ua1On6A2RwQGF82LO1tbdqo6pHbvq9Zo'
download_url = f'https://drive.google.com/uc?export=download&id={file_id}'

# Descargar el archivo Excel
response = requests.get(download_url)
response.raise_for_status()  # Para verificar que la descarga fue exitosa

# Leer el archivo Excel descargado directamente desde la respuesta
excel_data = BytesIO(response.content)
df = pd.read_excel(excel_data, sheet_name='Sitios Bogota')

# Leer el archivo Excel con pandas
print(df.head())


# Configurar el bot
BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError("No se encontró el token del bot. Asegúrate de tener un archivo .env con BOT_TOKEN=tu_token")

bot = telebot.TeleBot(BOT_TOKEN)

def crear_enlace_maps(latitud, longitud):
    return f"https://www.google.com/maps/search/?api=1&query={latitud},{longitud}"

def buscar_por_id(id):
    print(f"Buscando ID: {id}")
    
    # Búsqueda en el DataFrame de pandas
    for idx, row in df.iterrows():
        if str(row['ID']).strip() == id.strip():
            latitud, longitud = row['Columna1'], row['Columna2']
            maps_link = crear_enlace_maps(latitud, longitud)
            return (f"Codigo de Maximo: {row['COD MAX']}\nID: {row['ID']}\nNombre: {row['NOMBRE']}\nDirección: {row['DIRECCION']}\nCuenta NIC: {row['CTA NIC']}"
                    f"\nPto 0/1/0: {row['TX A']}\nPto 0/2/0: {row['TX B']}\nLlaves: {row['LLAVES']}\nNotas: {row['OBSERVACIONES']}"
                    f"\nCoordenadas: {latitud}, {longitud}\n"
                    f"\nUbicación en Maps: {maps_link}")
    
    print(f"ID no encontrado: {id}")
    return "No se encontró el ID especificado."

def buscar_por_nombre(nombre):
    print(f"Buscando nombre: {nombre}")

    # Búsqueda en el DataFrame de pandas
    for idx, row in df.iterrows():
        if row['Nombre'].lower().strip() == nombre.lower().strip():
            latitud, longitud = row['Latitud'], row['Longitud']
            maps_link = crear_enlace_maps(latitud, longitud)
            return (f"Codigo de Maximo: {row['Codigo']}\nID: {row['ID']}\nNombre: {row['Nombre']}\nDirección: {row['Direccion']}\nCuenta NIC: {row['Cuenta NIC']}"
                    f"\nPto 0/1/0: {row['Pto 0/1/0']}\nPto 0/2/0: {row['Pto 0/2/0']}\nLlaves: {row['Llaves']}\nNotas: {row['Notas']}"
                    f"\nCoordenadas: {latitud}, {longitud}\n"
                    f"\nUbicación en Maps: {maps_link}")
    
    print(f"Nombre no encontrado: {nombre}")
    return "No se encontró el nombre especificado."

# Función para mostrar el menú interactivo con botones de opción
@bot.message_handler(commands=['buscar'])
def show_menu(message):
    # Crear botones para buscar por ID o por nombre
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_id = types.InlineKeyboardButton("Buscar por ID", callback_data="buscar_id")
    btn_nombre = types.InlineKeyboardButton("Buscar por Nombre", callback_data="buscar_nombre")
    markup.add(btn_id, btn_nombre)
    
    # Enviar mensaje con los botones
    bot.send_message(message.chat.id, "Selecciona una opción:", reply_markup=markup)

# Función que maneja los botones seleccionados
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "buscar_id":
        msg = bot.send_message(call.message.chat.id, "Ingresa el ID:")
        bot.register_next_step_handler(msg, process_id)  # Procesar la entrada del usuario para ID
    elif call.data == "buscar_nombre":
        msg = bot.send_message(call.message.chat.id, "Ingresa el nombre:")
        bot.register_next_step_handler(msg, process_name)  # Procesar la entrada del usuario para nombre

# Función para procesar el ID ingresado por el usuario
def process_id(message):
    id = message.text.strip()  # Limpiar espacios
    resultado = buscar_por_id(id)
    bot.reply_to(message, resultado)

# Función para procesar el nombre ingresado por el usuario
def process_name(message):
    nombre = message.text.strip().lower()  # Convertir a minúsculas y limpiar espacios
    resultado = buscar_por_nombre(nombre)
    bot.reply_to(message, resultado)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    print(f"Comando recibido: {message.text}")
    bot.reply_to(message, "Bienvenido! Usa /buscar para comenzar y seleccionar entre ID o Nombre.")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    print(f"Mensaje recibido: {message.text}")
    bot.reply_to(message, "No entiendo ese comando. Por favor, usa /start para ver las instrucciones.")

# Iniciar el bot
try:
    print("Bot iniciado. Presiona Ctrl+C para detener.")
    bot.polling()
except Exception as e:
    print(f"Error en la ejecución del bot: {e}")
finally:
    print("Bot detenido.")
