import os
import time
from telegram import Bot, Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from solana.rpc.api import Client
from solana.transaction import Transaction
from solana.account import Account
from solana.system_program import TransferParams, transfer

# Config
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = "YOUR_TELEGRAM_CHAT_ID"  # Get from @userinfobot
ADMIN_WALLET = "YOUR_MAIN_SOLANA_WALLET"
WALLETS = {
    "Wallet1": {
        "address": "USER1_SOLANA_ADDRESS",
        "private_key": "USER1_PRIVATE_KEY"  # Insecure! Use env vars in production
    }
}

# Initialize
solana_client = Client("https://api.mainnet-beta.solana.com")
bot = Bot(token=BOT_TOKEN)

def start(update: Update, context: CallbackContext):
    update.message.reply_text("🟢 Solana Auto-Transfer Bot is running!")

def check_balances(context: CallbackContext):
    for name, wallet in WALLETS.items():
        balance = solana_client.get_balance(wallet["address"]).value
        if balance > 5000:  # Minimum transfer amount
            # Transfer logic here (simplified)
            bot.send_message(
                chat_id=ADMIN_CHAT_ID,
                text=f"💰 New deposit in {name}: {balance/1e9} SOL"
            )

def main():
    updater = Updater(BOT_TOKEN)
    updater.dispatcher.add_handler(CommandHandler("start", start))
    
    # Check balances every 10 minutes
    job_queue = updater.job_queue
    job_queue.run_repeating(check_balances, interval=600, first=0)
    
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
