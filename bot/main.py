from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
import pandas as pd
import joblib

# Token de Telegram
TOKEN = '7692227565:AAEC7nLwV-iCxG8RpwzjohW_b-3c7Q3546w'

# Cargar modelo entrenado
modelo = joblib.load("ml/price_predictor_model.pkl")

# Cargar dataset único en español
productos_df = pd.read_csv("datasets/productos_es.csv")
productos_df = productos_df.dropna(subset=[
    "prod_name", "prod_name_long", "prod_brand", "category", "subcategory", "tags", "prod_unit_price"
])
productos_df = productos_df.rename(columns={"prod_unit_price": "price"})

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"¡Hola {update.effective_user.first_name}! 🛒\n"
        f"Puedes escribirme el nombre de un producto o una categoría, y te daré el precio estimado."
    )

# Mensajes del usuario
async def texto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mensaje = update.message.text.lower()
    user = update.effective_user.first_name
    print(f"[{user}] escribió: {mensaje}")

    # Saludos
    saludos = ["hola", "hi", "buenas", "buenos días", "buenas tardes", "buenas noches"]
    if any(s in mensaje for s in saludos):
        await update.message.reply_text(f"👋 ¡Hola {user}! ¿Qué producto o categoría deseas buscar?")
        return

    # Buscar coincidencia en título largo o tags
    productos = productos_df[
        productos_df["prod_name_long"].str.lower().str.contains(mensaje, na=False)
        | productos_df["tags"].str.lower().str.contains(mensaje, na=False)
        | productos_df["category"].str.lower().str.contains(mensaje, na=False)
    ]

    if not productos.empty:
        prod = productos.sample(1).iloc[0]
        respuesta = (
            f"🛍️ *{prod['prod_name_long']}*\n"
            f"🏷️ Marca: {prod['prod_brand']}\n"
            f"📦 Categoría: {prod['category']} > {prod['subcategory']}\n"
            f"💬 Tags: {prod['tags']}\n"
            f"💵 Precio real: ${prod['price']}"
        )
    else:
        # Si no se encuentra, predecir con ML
        ejemplo = productos_df.sample(1).iloc[0]
        entrada = {
            "prod_name": mensaje,
            "prod_name_long": mensaje,
            "prod_brand": ejemplo["prod_brand"],
            "category": ejemplo["category"],
            "subcategory": ejemplo["subcategory"],
            "tags": ejemplo["tags"]
        }
        df_entrada = pd.DataFrame([entrada])
        pred = modelo.predict(df_entrada)[0]

        respuesta = (
            f"🔍 No encontré coincidencia exacta.\n"
            f"🤖 Precio estimado por IA: *${round(pred, 2)}*"
        )

    await update.message.reply_text(respuesta, parse_mode="Markdown")

# Inicializar el bot
if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, texto))
    print("🤖 Bot corriendo. Ve a Telegram y escríbele.")
    app.run_polling()
