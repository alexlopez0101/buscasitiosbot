from flask import Flask, request
import telebot
import os
from dotenv import load_dotenv
from telebot import types
import requests
import pandas as pd
from io import BytesIO

# Cargar variables de entorno
load_dotenv()

# Configurar el bot (una sola vez)
TOKEN = os.getenv("BOT_TOKEN")
if TOKEN is None:
    raise ValueError("BOT_TOKEN no está configurado.")
    
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Cargar datos de Excel
file_id = '1Ua1On6A2RwQGF82LO1tbdqo6pHbvq9Zo'
download_url = f'https://drive.google.com/uc?export=download&id={file_id}'

try:
    response = requests.get(download_url)
    response.raise_for_status()
    excel_data = BytesIO(response.content)
    df = pd.read_excel(excel_data, sheet_name='Sitios Bogota')
    print("Excel cargado exitosamente")
except Exception as e:
    print(f"Error cargando Excel: {e}")
    raise

def crear_enlace_maps(latitud, longitud):
    return f"https://www.google.com/maps/search/?api=1&query={latitud},{longitud}"

# Función para buscar por ID
def buscar_por_id(id, chat_id):
    print(f"Buscando ID: {id}")
    try:
        resultado = df[df['ID'].astype(str).str.strip() == str(id).strip()]
        if not resultado.empty:
            row = resultado.iloc[0]
            latitud, longitud = row['Columna1'], row['Columna2']
            maps_link = crear_enlace_maps(latitud, longitud)
            return (f"Codigo de Maximo: {row['COD MAX']}\nID: {row['ID']}\n"
                   f"Nombre: {row['NOMBRE']}\nDirección: {row['DIRECCION']}\n"
                   f"Cuenta NIC: {row['CTA NIC']}\nPto 0/1/0: {row['TX A']}\n"
                   f"Pto 0/2/0: {row['TX B']}\nLlaves: {row['LLAVES']}\n"
                   f"Notas: {row['OBSERVACIONES']}\n"
                   f"Coordenadas: {latitud}, {longitud}\n"
                   f"\nUbicación en Maps: {maps_link}")
        
        markup = types.InlineKeyboardMarkup(row_width=2)
        btn_volver = types.InlineKeyboardButton("Volver a buscar", callback_data="buscar_otro_id")
        markup.add(btn_volver)
        bot.send_message(chat_id, "No se encontró el ID especificado. ¿Quieres intentar nuevamente?", 
                        reply_markup=markup)
        return None
    except Exception as e:
        print(f"Error en búsqueda por ID: {e}")
        return f"Ocurrió un error durante la búsqueda: {str(e)}"

# Función para buscar por Nombre
def buscar_por_nombre(nombre, chat_id):
    print(f"Buscando nombre: {nombre}")
    try:
        resultado = df[df['NOMBRE'].str.lower().str.strip() == nombre.lower().strip()]
        if not resultado.empty:
            row = resultado.iloc[0]
            latitud, longitud = row['Columna1'], row['Columna2']
            maps_link = crear_enlace_maps(latitud, longitud)
            return (f"Codigo de Maximo: {row['COD MAX']}\nID: {row['ID']}\n"
                   f"Nombre: {row['NOMBRE']}\nDirección: {row['DIRECCION']}\n"
                   f"Cuenta NIC: {row['CTA NIC']}\nPto 0/1/0: {row['TX A']}\n"
                   f"Pto 0/2/0: {row['TX B']}\nLlaves: {row['LLAVES']}\n"
                   f"Notas: {row['OBSERVACIONES']}\n"
                   f"Coordenadas: {latitud}, {longitud}\n"
                   f"\nUbicación en Maps: {maps_link}")
        
        markup = types.InlineKeyboardMarkup(row_width=2)
        btn_volver = types.InlineKeyboardButton("Volver a buscar", callback_data="buscar_otro_nombre")
        markup.add(btn_volver)
        bot.send_message(chat_id, "No se encontró el nombre especificado. ¿Quieres intentar nuevamente?", 
                        reply_markup=markup)
        return None
    except Exception as e:
        print(f"Error en búsqueda por nombre: {e}")
        return f"Ocurrió un error durante la búsqueda: {str(e)}"

# Un solo manejador de callbacks
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    try:
        if call.data == "buscar_id":
            msg = bot.send_message(call.message.chat.id, "Ingresa el ID:")
            bot.register_next_step_handler(msg, process_id)
        elif call.data == "buscar_nombre":
            msg = bot.send_message(call.message.chat.id, "Ingresa el nombre:")
            bot.register_next_step_handler(msg, process_name)
        elif call.data == "buscar_otro_id":
            msg = bot.send_message(call.message.chat.id, "Ingresa el ID nuevamente:")
            bot.register_next_step_handler(msg, process_id)
        elif call.data == "buscar_otro_nombre":
            msg = bot.send_message(call.message.chat.id, "Ingresa el nombre nuevamente:")
            bot.register_next_step_handler(msg, process_name)
    except Exception as e:
        print(f"Error en callback_query: {e}")

def process_id(message):
    try:
        id = message.text.strip()
        resultado = buscar_por_id(id, message.chat.id)
        if resultado:
            bot.reply_to(message, resultado)
    except Exception as e:
        print(f"Error en process_id: {e}")
        bot.reply_to(message, "Ocurrió un error al procesar tu solicitud.")

def process_name(message):
    try:
        nombre = message.text.strip()
        resultado = buscar_por_nombre(nombre, message.chat.id)
        if resultado:
            bot.reply_to(message, resultado)
    except Exception as e:
        print(f"Error en process_name: {e}")
        bot.reply_to(message, "Ocurrió un error al procesar tu solicitud.")

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    try:
        print(f"Comando recibido: {message.text}")
        bot.reply_to(message, "Bienvenido! Usa /buscar para comenzar y seleccionar entre ID o Nombre.")
    except Exception as e:
        print(f"Error en send_welcome: {e}")

@bot.message_handler(commands=['buscar'])
def show_menu(message):
    try:
        markup = types.InlineKeyboardMarkup(row_width=2)
        btn_id = types.InlineKeyboardButton("Buscar por ID", callback_data="buscar_id")
        btn_nombre = types.InlineKeyboardButton("Buscar por Nombre", callback_data="buscar_nombre")
        markup.add(btn_id, btn_nombre)
        bot.send_message(message.chat.id, "Selecciona una opción:", reply_markup=markup)
    except Exception as e:
        print(f"Error en show_menu: {e}")

@app.route("/" + TOKEN, methods=['POST'])
def getMessage():
    try:
        json_str = request.get_data().decode('UTF-8')
        print(f"Actualización recibida: {json_str}")
        update = telebot.types.Update.de_json(json_str)
        bot.process_new_updates([update])
        return "¡OK!", 200
    except Exception as e:
        print(f"Error al procesar la actualización: {e}")
        return "Error", 500

@app.route("/")
def webhook():
    try:
        bot.remove_webhook()
        # Asegúrate de reemplazar la URL con tu dominio de Render
        webhook_url = f"https://buscasitiosbot.onrender.com/{TOKEN}"
        bot.set_webhook(url=webhook_url)
        return "Webhook configurado!", 200
    except Exception as e:
        print(f"Error configurando webhook: {e}")
        return "Error", 500

if __name__ == "__main__":
    # Iniciar la aplicación en el puerto que Render asigna
    port = int(os.environ.get('PORT', 5000))
    app.run(host="0.0.0.0", port=port)