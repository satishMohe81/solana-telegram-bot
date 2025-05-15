import os
import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

# Enable verbose logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def start(update: Update, context: CallbackContext):
    update.message.reply_text("🚀 Bot is alive!")

def main():
    TOKEN = os.getenv("TELEGRAM_TOKEN")
    if not TOKEN:
        raise ValueError("No TELEGRAM_TOKEN set in environment!")

    updater = Updater(TOKEN)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    
    logging.info("Starting polling...")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
