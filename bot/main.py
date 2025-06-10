from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
import requests

# Token del bot
TOKEN = '7692227565:AAEC7nLwV-iCxG8RpwzjohW_b-3c7Q3546w'

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    nombre = update.effective_user.first_name
    await update.message.reply_text(
        f"¡Hola {nombre}! 🛒\n"
        f"Escríbeme el nombre de un producto y te daré una sugerencia desde nuestra base de datos."
    )

# Manejo de mensajes
async def texto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mensaje = update.message.text.strip().lower()
    nombre_usuario = update.effective_user.first_name
    print(f"[{nombre_usuario}] escribió: {mensaje}")

    saludos = ["hola", "hi", "buenas", "buenos días", "buenas tardes", "buenas noches"]
    if any(s in mensaje for s in saludos):
        await update.message.reply_text(f"👋 ¡Hola {nombre_usuario}! ¿Qué producto deseas buscar?")
        return

    try:
        # Llamar a la API de sugerencias
        response = requests.get("http://localhost:8000/api/sugerir-producto", params={"query": mensaje})
        response.raise_for_status()
        datos = response.json()
        print("Respuesta de la API:", datos)

        # Soportar tanto lista como diccionario
        if isinstance(datos, list) and len(datos) > 0:
            prod = datos[0]
        elif isinstance(datos, dict) and datos:
            prod = datos
        else:
            respuesta = f"🔍 Lo siento {nombre_usuario}, no encontré sugerencias para: '{mensaje}'."
            await update.message.reply_text(respuesta)
            return

        # Asegurar conversión segura de datos
        nombre = str(prod.get('nombre', 'N/A'))
        marca = str(prod.get('marca', 'N/A'))
        categoria = str(prod.get('categoria', 'N/A'))
        tags = str(prod.get('tags', 'N/A'))
        precio = str(prod.get('precio_sugerido', 'N/A'))

        # Construir respuesta segura (sin parse_mode)
        respuesta = (
            f"🔎 ¡{nombre_usuario}, encontré esto para ti!\n\n"
            f"🛍️ Producto: {nombre}\n"
            f"🏷️ Marca: {marca}\n"
            f"📦 Categoría: {categoria}\n"
            f"💬 Tags: {tags}\n"
            f"💵 Precio sugerido: $ {precio}"
        )

    except Exception as e:
        print(f"❌ Error al contactar la API: {e}")
        respuesta = f"⚠️ Ocurrió un error, {nombre_usuario}. Intenta más tarde."

    await update.message.reply_text(respuesta)

# Inicializar el bot
if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, texto))
    print("🤖 Bot corriendo. Ve a Telegram y escríbele.")
    app.run_polling()
