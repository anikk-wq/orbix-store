import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, PreCheckoutQueryHandler,
    MessageHandler, ContextTypes, filters
)

logging.basicConfig(level=logging.INFO)
TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
PAYMENT_PROVIDER_TOKEN = os.getenv("PAYMENT_PROVIDER_TOKEN", "")

# Demo catalogue: edit these examples before selling real products.
PRODUCTS = {
    "starter": {
        "name": "Starter Pack",
        "description": "A sample digital product. Replace with your own lawful product.",
        "stars": 50,
        "file_id": os.getenv("STARTER_FILE_ID", "")
    },
    "pro": {
        "name": "Pro Pack",
        "description": "A sample digital product. Replace with your own lawful product.",
        "stars": 120,
        "file_id": os.getenv("PRO_FILE_ID", "")
    }
}

def home_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🛍️ Browse Products", callback_data="products")],
        [InlineKeyboardButton("📦 My Orders", callback_data="orders"),
         InlineKeyboardButton("ℹ️ Help", callback_data="help")]
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✨ Welcome to Wealthora Shop\n\nChoose an option below to explore our digital products.",
        reply_markup=home_keyboard()
    )

async def show_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = []
    for key, item in PRODUCTS.items():
        keyboard.append([InlineKeyboardButton(
            f"💎 {item['name']} — {item['stars']} ⭐",
            callback_data=f"buy:{key}"
        )])
    keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data="home")])
    await query.edit_message_text(
        "🛍️ **Our Digital Products**\n\nChoose a product to see details and checkout with Telegram Stars.",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

async def product_detail(update: Update, context: ContextTypes.DEFAULT_TYPE, key: str):
    query = update.callback_query
    item = PRODUCTS[key]
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"⭐ Buy for {item['stars']} Stars", callback_data=f"checkout:{key}")],
        [InlineKeyboardButton("⬅️ Products", callback_data="products")]
    ])
    await query.edit_message_text(
        f"💎 {item['name']}\n\n{item['description']}\n\nPrice: {item['stars']} Telegram Stars",
        reply_markup=keyboard
    )

async def checkout(update: Update, context: ContextTypes.DEFAULT_TYPE, key: str):
    query = update.callback_query
    item = PRODUCTS[key]
    # Telegram Stars invoices must use currency XTR and no provider token.
    await context.bot.send_invoice(
        chat_id=query.message.chat_id,
        title=item["name"],
        description=item["description"],
        payload=f"digital:{key}:{query.from_user.id}",
        provider_token="",
        currency="XTR",
        prices=[LabeledPrice(item["name"], item["stars"])],
        start_parameter=f"buy-{key}"
    )
    await query.answer("Checkout opened")

async def precheckout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.pre_checkout_query.answer(ok=True)

async def successful_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    payment = update.message.successful_payment
    payload = payment.invoice_payload
    parts = payload.split(":")
    if len(parts) != 3 or parts[0] != "digital":
        await update.message.reply_text("Payment received, but the order needs admin review. Please contact support.")
        return
    key = parts[1]
    buyer_id = update.effective_user.id
    item = PRODUCTS.get(key)
    if not item:
        await update.message.reply_text("Payment received. Please contact support for delivery.")
        return
    file_id = item.get("file_id")
    if file_id:
        try:
            await context.bot.send_document(chat_id=buyer_id, document=file_id,
                                            caption=f"✅ Payment confirmed — {item['name']}")
        except Exception:
            await update.message.reply_text("✅ Payment received. Automatic delivery failed; please contact support.")
    else:
        await update.message.reply_text(
            f"✅ Payment received for {item['name']}!\n\n"
            "Automatic delivery is not configured yet. Please contact the shop admin."
        )
    if ADMIN_ID:
        await context.bot.send_message(
            ADMIN_ID,
            f"🧾 New paid order\nProduct: {item['name']}\nBuyer ID: {buyer_id}\n"
            f"Charge ID: {payment.telegram_payment_charge_id}"
        )

async def callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data or ""
    if data == "home":
        await query.answer()
        await query.edit_message_text(
            "✨ Welcome to Wealthora Shop\n\nChoose an option below:",
            reply_markup=home_keyboard()
        )
    elif data == "products":
        await show_products(update, context)
    elif data.startswith("buy:"):
        await query.answer()
        key = data.split(":", 1)[1]
        if key in PRODUCTS:
            await product_detail(update, context, key)
    elif data.startswith("checkout:"):
        key = data.split(":", 1)[1]
        if key in PRODUCTS:
            await checkout(update, context, key)
    elif data == "orders":
        await query.answer()
        await query.edit_message_text(
            "📦 Order history will be added in the next version. Successful payments are sent to the admin.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="home")]])
        )
    elif data == "help":
        await query.answer()
        await query.edit_message_text(
            "ℹ️ Need help? Contact the shop admin.\n\nOnly buy products you understand. Keep your payment receipts.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="home")]])
        )
    else:
        await query.answer()

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Use /start to open the shop menu.")

def main():
    if not TOKEN:
        raise RuntimeError("Set BOT_TOKEN as an environment variable.")
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(callbacks))
    app.add_handler(PreCheckoutQueryHandler(precheckout))
    app.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, unknown))
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
