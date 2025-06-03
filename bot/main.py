from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
import pandas as pd
import random

# ⚠️ Reemplaza esto con tu token real del bot
TOKEN = '7692227565:AAEC7nLwV-iCxG8RpwzjohW_b-3c7Q3546w'

# 📂 Cargar el dataset de productos de Amazon
df = pd.read_csv("datasets/amazon_products.csv")

# 🧼 Limpiar datos (asegura que haya títulos y precios)
df = df[["title", "price"]].dropna().reset_index(drop=True)

# 👋 Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "¡Hola! Soy tu asistente de compras 🛍️.\n"
        "Escríbeme qué producto deseas y te daré una sugerencia real de Amazon."
    )

# 💬 Respuesta a texto
async def texto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mensaje = update.message.text
    user = update.effective_user.first_name
    print(f"[Texto recibido de {user}]: {mensaje}")

    # 🛍️ Seleccionar un producto aleatorio del dataset
    producto = df.sample(1).iloc[0]
    nombre = producto["title"]
    precio = producto["price"]

    respuesta = f"🔎 Según lo que buscas, te recomiendo:\n\n🛍️ *{nombre}*\n💵 Precio estimado: ${precio}"
    await update.message.reply_text(respuesta, parse_mode="Markdown")

# 🚀 Iniciar el bot
if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler('start', start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, texto))

    print("🤖 Bot corriendo... ve a Telegram y escribe /start.")
    app.run_polling()
