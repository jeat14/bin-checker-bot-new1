from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
import requests

TOKEN = "7684349405:AAFZHHlXTVwy7dOI54az9pv8zkjwHGWQXUY"

async def get_bin_info(bin_number):
    headers = {
        'Accept-Version': '3',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(f'https://bins.antipublic.cc/bins/{bin_number}', headers=headers)
        if response.status_code == 200:
            return response.json()
    except:
        pass
        
    try:
        response = requests.get(f'https://lookup.binlist.net/{bin_number}')
        if response.status_code == 200:
            return response.json()
    except:
        pass
    
    return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    commands = [
        BotCommand("start", "Start the bot"),
        BotCommand("help", "Show help menu"),
        BotCommand("about", "About this bot"),
        BotCommand("example", "Show example BINs")
    ]
    await context.bot.set_my_commands(commands)
    
    welcome_message = (
        "🏦 Welcome to Premium BIN Checker!\n\n"
        "Commands:\n"
        "/start - Start the bot\n"
        "/help - Show help menu\n"
        "/about - About this bot\n"
        "/example - Show example BINs\n\n"
        "Just send me any 6-digit BIN number to check!"
    )
    await update.message.reply_text(welcome_message)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "📚 How to use BIN Checker:\n\n"
        "1. Send any 6-digit BIN number\n"
        "2. Get detailed card information\n\n"
        "Commands:\n"
        "/start - Start the bot\n"
        "/help - Show this help menu\n"
        "/about - About this bot\n"
        "/example - Show example BINs\n\n"
        "Information provided:\n"
        "✓ Card Brand\n"
        "✓ Card Type\n"
        "✓ Card Level\n"
        "✓ Bank Details\n"
        "✓ Country Info\n"
        "✓ And more..."
    )
    await update.message.reply_text(help_text)

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    about_text = (
        "ℹ️ About BIN Checker\n\n"
        "This bot helps you check card BIN information.\n\n"
        "Features:\n"
        "• Fast BIN lookup\n"
        "• Detailed information\n"
        "• Multiple data sources\n"
        "• 24/7 availability\n\n"
        "Send /help to learn how to use the bot!"
    )
    await update.message.reply_text(about_text)

async def example_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    example_text = (
        "🔢 Example BINs to test:\n\n"
        "• 451015 - Visa\n"
        "• 402944 - Visa\n"
        "• 549184 - Mastercard\n"
        "• 524462 - Mastercard\n"
        "• 377481 - American Express\n"
        "• 601101 - Discover\n\n"
        "Just send any of these numbers to test!"
    )
    await update.message.reply_text(example_text)

async def check_bin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bin_number = update.message.text.strip()
    
    if not bin_number.isdigit() or len(bin_number) < 6:
        await update.message.reply_text(
            "❌ Invalid BIN!\n\n"
            "Please send first 6 digits of card number\n"
            "Use /example to see sample BINs"
        )
        return

    bin_number = bin_number[:6]
    
    data = await get_bin_info(bin_number)
    
    if data:
        try:
            # Get card type and prepaid status
            card_type = str(data.get('type', '')).upper()
            if 'PREPAID' in card_type:
                prepaid_text = "YES - PREPAID CARD ✅"
            elif 'DEBIT' in card_type:
                prepaid_text = "NO - DEBIT CARD 💳"
            elif 'CREDIT' in card_type:
                prepaid_text = "NO - CREDIT CARD 💳"
            else:
                prepaid_text = "UNKNOWN ❓"
            
            result = (
                f"🔍 BIN INFORMATION: {bin_number}\n"
                f"━━━━━━━━━━━━━━━\n\n"
                f"💳 CARD DETAILS:\n"
                f"• Brand: {data.get('scheme', '').upper() or data.get('brand', 'N/A').upper()}\n"
                f"• Type: {card_type}\n"
                f"• Category: {data.get('level', 'N/A').upper()}\n"
                f"• Prepaid: {prepaid_text}\n\n"
                f"🏦 BANK INFO:\n"
                f"• Name: {data.get('bank', {}).get('name', data.get('bank', 'N/A'))}\n"
                f"• Website: {data.get('bank', {}).get('url', 'www.bank.com')}\n"
                f"• Phone: {data.get('bank', {}).get('phone', '+1234567890')}\n\n"
                f"📍 COUNTRY INFO:\n"
                f"• Country: {data.get('country', {}).get('name', data.get('country', 'N/A'))}\n"
                f"• Currency: {data.get('country', {}).get('currency', 'USD')}\n"
                f"• Region: {data.get('country', {}).get('region', 'N/A')}\n\n"
                f"✨ EXTRA INFO:\n"
                f"• Valid Length: 16\n"
                f"• Security: CVV/CVC\n"
                f"━━━━━━━━━━━━━━━"
            )
            
            keyboard = [
                [InlineKeyboardButton("🔄 Check Another", callback_data='check_another')],
                [InlineKeyboardButton("❓ Help", callback_data='help')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(result, reply_markup=reply_markup)
        except Exception as e:
            await update.message.reply_text(
                "❌ Error processing BIN data\n"
                "Try another BIN or use /example"
            )
    else:
        await update.message.reply_text(
            "❌ BIN not found in database\n"
            "Try another BIN or use /example"
        )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == 'check_another':
        await query.message.reply_text("Send another BIN:")
    elif query.data == 'help':
        await help_command(update, context)

def main():
    application = Application.builder().token(TOKEN).build()

    # Setup handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("about", about_command))
    application.add_handler(CommandHandler("example", example_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_bin))
    application.add_handler(CallbackQueryHandler(button_callback))

    print("Premium BIN Checker Bot is starting...")
    application.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
