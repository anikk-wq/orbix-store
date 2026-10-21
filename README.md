# Premium Shopping Bot starter

This is a starter template for a Telegram digital-products shop. It includes a simple product menu, inline buttons, Telegram Stars checkout, and optional delivery by Telegram file ID.

## Important
- Telegram requires **Telegram Stars (XTR)** for digital goods sold inside Telegram bots. Do not use UPI or crypto checkout inside the bot for those in-Telegram digital sales.
- This is a starter, not a finished production marketplace. It does not yet include persistent order history, refunds tooling, a database, or an admin dashboard.
- Keep `BOT_TOKEN` secret. Never commit it to GitHub.
- Free hosting is not guaranteed to provide uninterrupted 24/7 uptime.

## Configure
Set these environment variables in your hosting provider:
- `BOT_TOKEN`: token from @BotFather
- `ADMIN_ID`: your numeric Telegram user ID (optional but recommended)
- `STARTER_FILE_ID`: Telegram file ID for the Starter Pack delivery (optional)
- `PRO_FILE_ID`: Telegram file ID for the Pro Pack delivery (optional)

Edit `PRODUCTS` in `bot.py` to set product names, descriptions, and prices in Stars.

## Run
Python 3.11+ recommended:
```bash
pip install -r requirements.txt
python bot.py
```
