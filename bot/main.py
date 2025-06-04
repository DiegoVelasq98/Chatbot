from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
import pandas as pd
import joblib

# Token de Telegram
TOKEN = '7692227565:AAEC7nLwV-iCxG8RpwzjohW_b-3c7Q3546w'

# Cargar modelo ML entrenado
modelo = joblib.load("ml/price_predictor_model.pkl")

# Cargar datasets
productos_df = pd.read_csv("datasets/amazon_products.csv")
categorias_df = pd.read_csv("datasets/amazon_categories.csv")

# Limpieza
productos_df = productos_df.dropna(subset=[
    "title", "stars", "reviews", "price", "category_id", "isBestSeller", "boughtInLastMonth"
])
productos_df["isBestSeller"] = productos_df["isBestSeller"].astype(int)

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"¡Hola {update.effective_user.first_name}! 🛍️\n"
        f"Puedes escribirme el nombre de un producto o una categoría. Te daré una sugerencia y el precio estimado."
    )

# Mensajes
async def texto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mensaje = update.message.text.lower()
    user = update.effective_user.first_name
    print(f"[{user}] escribió: {mensaje}")

    # Respuesta si es un saludo
    saludos = ["hola", "hi", "buenas", "buenos días", "buenas tardes", "buenas noches"]
    if any(s in mensaje for s in saludos):
        saludo = f"👋 Hola {user} 😊, ¿qué producto o categoría deseas buscar?"
        await update.message.reply_text(saludo)
        return

    # Buscar producto por título
    productos = productos_df[productos_df["title"].str.lower().str.contains(mensaje)]

    # Buscar por categoría
    cat = categorias_df[categorias_df["category_name"].str.lower().str.contains(mensaje)]

    if not productos.empty:
        prod = productos.sample(1).iloc[0]
        respuesta = (
            f"🛍️ Producto encontrado:\n"
            f"*{prod['title']}*\n"
            f"💵 Precio: ${prod['price']}"
        )

    elif not cat.empty:
        cat_id = int(cat["id"].values[0])
        candidatos = productos_df[productos_df["category_id"] == cat_id]

        if not candidatos.empty:
            ejemplo = candidatos.sample(1).iloc[0]
            entrada = {
                "title": mensaje,
                "stars": ejemplo["stars"],
                "reviews": ejemplo["reviews"],
                "category_id": cat_id,
                "isBestSeller": ejemplo["isBestSeller"],
                "boughtInLastMonth": ejemplo["boughtInLastMonth"]
            }

            df_entrada = pd.DataFrame([entrada])
            pred = modelo.predict(df_entrada)[0]

            respuesta = (
                f"🔍 Categoría detectada: *{cat['category_name'].values[0]}*\n"
                f"🛍️ Producto de ejemplo: {ejemplo['title']}\n"
                f"💵 Precio estimado: ${round(pred, 2)}"
            )
        else:
            respuesta = "❌ No encontré productos en esa categoría."
    else:
        respuesta = "😔 No encontré coincidencias. Intenta con otra palabra."

    await update.message.reply_text(respuesta, parse_mode="Markdown")

# Inicializar bot
if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, texto))
    print("🤖 Bot corriendo. Ve a Telegram y escríbele.")
    app.run_polling()
