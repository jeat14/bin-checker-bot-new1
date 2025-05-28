import os
from flask import Flask
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, 
    CommandHandler, 
    ContextTypes, 
    MessageHandler, 
    filters,
    CallbackQueryHandler
)
import requests

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is Running!"

def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

TOKEN = "7684349405:AAFZHHlXTVwy7dOI54az9pv8zkjwHGWQXUY"

# Country and Currency mappings
COUNTRY_CODES = {
    'GB': 'United Kingdom 🇬🇧',
    'US': 'United States 🇺🇸',
    'CA': 'Canada 🇨🇦',
    'FR': 'France 🇫🇷',
    'DE': 'Germany 🇩🇪',
    'IT': 'Italy 🇮🇹',
    'ES': 'Spain 🇪🇸',
    'AU': 'Australia 🇦🇺',
    'JP': 'Japan 🇯🇵',
}

CURRENCY_CODES = {
    'GB': 'GBP (£)',
    'US': 'USD ($)',
    'CA': 'CAD ($)',
    'FR': 'EUR (€)',
    'DE': 'EUR (€)',
    'IT': 'EUR (€)',
    'ES': 'EUR (€)',
    'AU': 'AUD ($)',
    'JP': 'JPY (¥)',
}

REGIONS = {
    'GB': 'Europe',
    'US': 'North America',
    'CA': 'North America',
    'FR': 'Europe',
    'DE': 'Europe',
    'IT': 'Europe',
    'ES': 'Europe',
    'AU': 'Oceania',
    'JP': 'Asia',
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_message = (
        "🏦 BIN Checker\n\n"
        "Send any 6-digit BIN number\n"
        "Example: 601101"
    )
    await update.message.reply_text(welcome_message)

async def check_bin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bin_number = update.message.text.strip()
    
    if not bin_number.isdigit() or len(bin_number) < 6:
        await update.message.reply_text("❌ Send first 6 digits of card number")
        return

    bin_number = bin_number[:6]
    
    try:
        headers = {
            'Accept-Version': '3',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        url = f"https://bins.antipublic.cc/bins/{bin_number}"
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            
            # Get country code and enhanced info
            country_code = data.get('country', 'N/A')
            country_name = COUNTRY_CODES.get(country_code, data.get('country', 'N/A'))
            currency = CURRENCY_CODES.get(country_code, data.get('currency', 'N/A'))
            region = REGIONS.get(country_code, 'N/A')
            
            # Determine card type and prepaid status
            card_type = data.get('type', '').upper()
            if 'PREPAID' in card_type:
                prepaid_text = "YES - PREPAID CARD ✅"
            elif 'DEBIT' in card_type:
                prepaid_text = "NO - DEBIT CARD 💳"
            elif 'CREDIT' in card_type:
                prepaid_text = "NO - CREDIT CARD 💳"
            else:
                prepaid_text = "UNKNOWN ❓"
            
            # Get bank website and phone based on country
            bank_website = "www.bank.com"
            bank_phone = "+44 800 00 00 00" if country_code == 'GB' else "+1 800 000 0000"
            
            result = (
                f"🔍 BIN INFORMATION: {bin_number}\n"
                f"━━━━━━━━━━━━━━━\n\n"
                f"💳 CARD DETAILS:\n"
                f"• Brand: {data.get('brand', 'N/A').upper()}\n"
                f"• Type: {card_type}\n"
                f"• Category: {data.get('level', 'N/A').upper()}\n"
                f"• Prepaid: {prepaid_text}\n\n"
                f"🏦 BANK INFO:\n"
                f"• Name: {data.get('bank', 'N/A')}\n"
                f"• Website: {bank_website}\n"
                f"• Phone: {bank_phone}\n\n"
                f"📍 COUNTRY INFO:\n"
                f"• Country: {country_name}\n"
                f"• Currency: {currency}\n"
                f"• Region: {region}\n\n"
                f"✨ EXTRA INFO:\n"
                f"• Valid Length: 16\n"
                f"• Security: CVV/CVC\n"
                f"━━━━━━━━━━━━━━━"
            )
            
            keyboard = [[InlineKeyboardButton("🔄 Check Another", callback_data='check_another')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(result, reply_markup=reply_markup)
        else:
            await update.message.reply_text("❌ BIN not found")
            
    except Exception as e:
        await update.message.reply_text("❌ Error checking BIN")

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == 'check_another':
        await query.message.reply_text("Send another BIN:")

def main():
    # Start Flask in a separate thread
    Thread(target=run_flask).start()
    
    # Configure the bot with dropout
    application = (
        ApplicationBuilder()
        .token(TOKEN)
        .concurrent_updates(True)
        .connect_timeout(30)
        .read_timeout(30)
        .write_timeout(30)
        .pool_timeout(30)
        .build()
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_bin))
    application.add_handler(CallbackQueryHandler(button_callback))
    
    print("BIN Checker Bot is starting...")
    application.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
