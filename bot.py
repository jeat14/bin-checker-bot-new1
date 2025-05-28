from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
import requests
import json

TOKEN = "7684349405:AAFZHHlXTVwy7dOI54az9pv8zkjwHGWQXUY"

async def get_bin_info(bin_number):
    apis = [
        {
            'url': f'https://lookup.binlist.net/{bin_number}',
            'headers': {'Accept-Version': '3'}
        },
        {
            'url': f'https://bins.su/api/{bin_number}',
            'headers': {'Authorization': 'Bearer sk_live_123'}
        },
        {
            'url': f'https://api.bintable.com/v1/{bin_number}',
            'headers': {'Authorization': 'Bearer 2c0e6171d6f07c7916ca69b0'}
        },
        {
            'url': f'https://bins-su-api.vercel.app/api/{bin_number}',
            'headers': {}
        },
        {
            'url': f'https://bin-check-dr4g.herokuapp.com/api/{bin_number}',
            'headers': {}
        }
    ]
    
    for api in apis:
        try:
            response = requests.get(api['url'], headers=api['headers'], timeout=5)
            if response.status_code == 200:
                data = response.json()
                
                # Get bank info
                bank_info = data.get('bank', {}) if isinstance(data.get('bank'), dict) else {'name': data.get('bank', 'N/A')}
                bank_name = bank_info.get('name', data.get('bank', 'N/A'))
                bank_url = bank_info.get('url', 'N/A')
                bank_phone = bank_info.get('phone', 'N/A')
                
                # Get country info
                country_info = data.get('country', {}) if isinstance(data.get('country'), dict) else {'name': data.get('country', 'N/A')}
                country_name = country_info.get('name', data.get('country', 'N/A'))
                country_emoji = country_info.get('emoji', '🌍')
                currency = country_info.get('currency', data.get('currency', 'N/A'))
                
                return {
                    'scheme': data.get('scheme', data.get('brand', 'N/A')).upper(),
                    'type': data.get('type', 'N/A').upper(),
                    'brand': data.get('brand', data.get('scheme', 'N/A')).upper(),
                    'category': data.get('category', data.get('level', 'N/A')).upper(),
                    'bank': {
                        'name': bank_name,
                        'url': bank_url,
                        'phone': bank_phone
                    },
                    'country': {
                        'name': f"{country_emoji} {country_name}",
                        'currency': currency,
                        'region': country_info.get('region', 'N/A')
                    },
                    'prepaid': data.get('prepaid', False)
                }
        except:
            continue
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
    checking_message = await update.message.reply_text("🔍 Checking BIN... Please wait.")
    
    data = await get_bin_info(bin_number)
    
    if data:
        try:
            # Get card type and prepaid status
            card_type = data.get('type', '').upper()
            if data.get('prepaid') or 'PREPAID' in card_type:
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
                f"• Brand: {data['scheme']}\n"
                f"• Type: {card_type}\n"
                f"• Category: {data.get('category', 'N/A')}\n"
                f"• Prepaid: {prepaid_text}\n\n"
                f"🏦 BANK INFO:\n"
                f"• Name: {data['bank']['name']}\n"
                f"• Website: {data['bank']['url']}\n"
                f"• Phone: {data['bank']['phone']}\n\n"
                f"📍 COUNTRY INFO:\n"
                f"• Country: {data['country']['name']}\n"
                f"• Currency: {data['country']['currency']}\n"
                f"• Region: {data['country']['region']}\n\n"
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
            
            await checking_message.delete()
            await update.message.reply_text(result, reply_markup=reply_markup)
        except Exception as e:
            await checking_message.delete()
            await update.message.reply_text(
                "❌ Error processing BIN data\n"
                "Try another BIN or use /example"
            )
    else:
        await checking_message.delete()
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
