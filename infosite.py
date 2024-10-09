import telebot
import openpyxl
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configurar el bot
BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError("No se encontró el token del bot. Asegúrate de tener un archivo .env con BOT_TOKEN=tu_token")

bot = telebot.TeleBot(BOT_TOKEN)

# Obtén la ruta del directorio actual del script
current_dir = os.path.dirname(os.path.abspath(__file__))

# Construye la ruta completa al archivo Excel
excel_path = os.path.join(current_dir, 'database.xlsx')

# Cargar el archivo Excel
try:
    workbook = openpyxl.load_workbook(excel_path, data_only=True)
    print(f"Archivo Excel cargado exitosamente: {excel_path}")
except FileNotFoundError:
    print(f"Error: No se encontró el archivo '{excel_path}'. Asegúrate de que el archivo exista en esta ubicación.")
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
            # Ahora usando las columnas 18 y 19 para las coordenadas
            latitud, longitud = row[18], row[19]  # Restamos 1 porque los índices en Python comienzan en 0
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
            # Ahora usando las columnas 18 y 19 para las coordenadas
            latitud, longitud = row[17], row[18]  # Restamos 1 porque los índices en Python comienzan en 0
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
try:
    print("Bot iniciado. Presiona Ctrl+C para detener.")
    bot.polling()
except Exception as e:
    print(f"Error en la ejecución del bot: {e}")
finally:
    print("Bot detenido.")