from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

TOKEN = '7692227565:AAEC7nLwV-iCxG8RpwzjohW_b-3c7Q3546w'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "¡Hola! Soy tu asistente de compras 🛍️.\n"
        "Escríbeme qué deseas o envíame una foto de un producto."
    )

async def texto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mensaje = update.message.text
    user = update.effective_user.first_name
    print(f"[Texto] {user}: {mensaje}")  # ⬅ Aquí ves el mensaje en la terminal
    await update.message.reply_text(f"🔎 Buscando productos relacionados con: '{mensaje}'...")


if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler('start', start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, texto))

    print("🤖 Bot corriendo. Ve a Telegram y escribe /start.")
    app.run_polling()
