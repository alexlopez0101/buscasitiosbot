from flask import Flask, request
import telebot
import os
from dotenv import load_dotenv
from telebot import types
import requests
import pandas as pd
from io import BytesIO

# Cargar el token del bot desde las variables de entorno
TOKEN = os.getenv("BOT_TOKEN")
if TOKEN is None:
    raise ValueError("BOT_TOKEN no está configurado.")
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Configurar el webhook para recibir actualizaciones
@app.route("/" + TOKEN, methods=['POST'])
def getMessage():
    json_str = request.get_data().decode('UTF-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "¡Recibido!", 200

# Ruta de prueba para asegurarnos de que el servidor esté funcionando
@app.route("/")
def index():
    return "El bot está funcionando", 200

# Función para crear el menú de opciones
def crear_menu_busqueda():
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_id = types.InlineKeyboardButton("Buscar por ID", callback_data="buscar_id")
    btn_nombre = types.InlineKeyboardButton("Buscar por Nombre", callback_data="buscar_nombre")
    markup.add(btn_id, btn_nombre)
    return markup


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

# Función para buscar por ID
def buscar_por_id(id, chat_id):
    print(f"Buscando ID: {id}")
    
    # Búsqueda en el DataFrame de pandas
    for idx, row in df.iterrows():
        if str(row['ID']).strip() == id.strip():
            latitud, longitud = row['Columna1'], row['Columna2']
            maps_link = crear_enlace_maps(latitud, longitud)
            return (f"Codigo de Maximo: {row['COD MAX']}\nID: {row['ID']}\nNombre: {row['NOMBRE']}\nDirección: {row['DIRECCION']}\nCuenta NIC: {row['CTA NIC']} "
                    f"\nPto 0/1/0: {row['TX A']}\nPto 0/2/0: {row['TX B']}\nLlaves: {row['LLAVES']}\nNotas: {row['OBSERVACIONES']}\nCoordenadas: {latitud}, {longitud}\n"
                    f"\nUbicación en Maps: {maps_link}")

    print(f"ID no encontrado: {id}")
    # Mostrar botón para volver a intentar la búsqueda
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_volver = types.InlineKeyboardButton("Volver a buscar", callback_data="buscar_otro_id")
    markup.add(btn_volver)
    
    bot.send_message(chat_id, "No se encontró el ID especificado. ¿Quieres intentar nuevamente?", reply_markup=markup)
    return None  # No devolver nada ya que estamos enviando el mensaje desde aquí.

# Función para buscar por Nombre
def buscar_por_nombre(nombre, chat_id):
    print(f"Buscando nombre: {nombre}")

    # Búsqueda en el DataFrame de pandas
    for idx, row in df.iterrows():
        if row['Nombre'].lower().strip() == nombre.lower().strip():
            latitud, longitud = row['Columna1'], row['Columna2']
            maps_link = crear_enlace_maps(latitud, longitud)
            return (f"Codigo de Maximo: {row['COD MAX']}\nID: {row['ID']}\nNombre: {row['NOMBRE']}\nDirección: {row['DIRECCION']}\nCuenta NIC: {row['CTA NIC']} "
                    f"\nPto 0/1/0: {row['TX A']}\nPto 0/2/0: {row['TX B']}\nLlaves: {row['LLAVES']}\nNotas: {row['OBSERVACIONES']}\nCoordenadas: {latitud}, {longitud}\n"
                    f"\nUbicación en Maps: {maps_link}")
    
    print(f"Nombre no encontrado: {nombre}")
    # Mostrar botón para volver a intentar la búsqueda
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_volver = types.InlineKeyboardButton("Volver a buscar", callback_data="buscar_otro_nombre")
    markup.add(btn_volver)
    
    bot.send_message(chat_id, "No se encontró el nombre especificado. ¿Quieres intentar nuevamente?", reply_markup=markup)
    return None  # No devolver nada ya que estamos enviando el mensaje desde aquí.

# Modificar los handlers de callback
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "buscar_id":
        msg = bot.send_message(call.message.chat.id, "Ingresa el ID:")
        bot.register_next_step_handler(msg, process_id)  # Procesar la entrada del usuario para ID
    elif call.data == "buscar_nombre":
        msg = bot.send_message(call.message.chat.id, "Ingresa el nombre:")
        bot.register_next_step_handler(msg, process_name)  # Procesar la entrada del usuario para nombre
    elif call.data == "buscar_otro_id":
        msg = bot.send_message(call.message.chat.id, "Ingresa el ID nuevamente:")
        bot.register_next_step_handler(msg, process_id)  # Procesar la entrada del usuario para ID
    elif call.data == "buscar_otro_nombre":
        msg = bot.send_message(call.message.chat.id, "Ingresa el nombre nuevamente:")
        bot.register_next_step_handler(msg, process_name)  # Procesar la entrada del usuario para nombre

# Modificar las funciones process_id y process_name
def process_id(message):
    id = message.text.strip()  # Limpiar espacios
    resultado = buscar_por_id(id, message.chat.id)
    if resultado:
        bot.reply_to(message, resultado)

def process_name(message):
    nombre = message.text.strip().lower()  # Convertir a minúsculas y limpiar espacios
    resultado = buscar_por_nombre(nombre, message.chat.id)
    if resultado:
        bot.reply_to(message, resultado)

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


# Función para manejar las opciones del menú
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
    buscar_por_id(id, message.chat.id)

# Función para procesar el nombre ingresado por el usuario
def process_name(message):
    nombre = message.text.strip().lower()  # Convertir a minúsculas y limpiar espacios
    buscar_por_nombre(nombre, message.chat.id)


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


if __name__ == "__main__":
    # Iniciar la aplicación en el puerto que Render asigna automáticamente
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
