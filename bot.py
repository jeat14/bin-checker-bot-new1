from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)
import requests
import json

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

def check_bin_lookup1(bin_number):
    try:
        url = f"https://lookup.binlist.net/{bin_number}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
    except:
        return None

def check_bin_lookup2(bin_number):
    try:
        url = f"https://bins.antipublic.cc/bins/{bin_number}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
    except:
        return None

def check_bin_lookup3(bin_number):
    try:
        url = f"https://bin-checker.net/api/{bin_number}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
    except:
        return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_message = (
        "🏦 Premium BIN Checker\n\n"
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
    
    # Try multiple BIN lookup services
    data = check_bin_lookup1(bin_number) or check_bin_lookup2(bin_number) or check_bin_lookup3(bin_number)
    
    if data:
        try:
            # Get card type and prepaid status
            card_type = data.get('type', '').upper()
            if 'PREPAID' in card_type:
                prepaid_text = "YES - PREPAID CARD ✅"
            elif 'DEBIT' in card_type:
                prepaid_text = "NO - DEBIT CARD 💳"
            elif 'CREDIT' in card_type:
                prepaid_text = "NO - CREDIT CARD 💳"
            else:
                prepaid_text = "UNKNOWN ❓"
            
            # Get country info
            country_code = data.get('country', {}).get('code', 'N/A')
            country_name = COUNTRY_CODES.get(country_code, data.get('country', {}).get('name', 'N/A'))
            currency = CURRENCY_CODES.get(country_code, data.get('country', {}).get('currency', 'N/A'))
            
            result = (
                f"🔍 BIN INFORMATION: {bin_number}\n"
                f"━━━━━━━━━━━━━━━\n\n"
                f"💳 CARD DETAILS:\n"
                f"• Brand: {data.get('scheme', '').upper() or data.get('brand', 'N/A').upper()}\n"
                f"• Type: {card_type}\n"
                f"• Category: {data.get('brand', 'N/A').upper()}\n"
                f"• Prepaid: {prepaid_text}\n\n"
                f"🏦 BANK INFO:\n"
                f"• Name: {data.get('bank', {}).get('name', 'N/A')}\n"
                f"• Website: {data.get('bank', {}).get('url', 'N/A')}\n"
                f"• Phone: {data.get('bank', {}).get('phone', 'N/A')}\n\n"
                f"📍 COUNTRY INFO:\n"
                f"• Country: {country_name}\n"
                f"• Currency: {currency}\n"
                f"• Region: {data.get('country', {}).get('region', 'N/A')}\n\n"
                f"✨ EXTRA INFO:\n"
                f"• Valid Length: {data.get('number', {}).get('length', '16')}\n"
                f"• Security: CVV/CVC\n"
                f"━━━━━━━━━━━━━━━"
            )
            
            keyboard = [[InlineKeyboardButton("🔄 Check Another", callback_data='check_another')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(result, reply_markup=reply_markup)
        except Exception as e:
            await update.message.reply_text("❌ Error processing BIN data")
    else:
        await update.message.reply_text("❌ BIN not found in database")

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == 'check_another':
        await query.message.reply_text("Send another BIN:")

def main():
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_bin))
    application.add_handler(CallbackQueryHandler(button_callback))

    print("Premium BIN Checker Bot is starting...")
    application.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
