"""
Main entry point for SearchTruth Telegram Bot
"""
import logging
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters

from config import BOT_TOKEN
from bot_handlers import (
    start_command, main_menu_callback, quran_search_callback,
    quran_translation_callback, hadith_search_callback,
    hadith_collection_callback, prayer_country_callback,
    dictionary_search_callback, dictionary_type_callback,
    help_command, handle_quran_search, handle_hadith_search,
    handle_dictionary_search, handle_quick_search
)

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def error_handler(update, context):
    """Log errors and send user-friendly message"""
    logger.error(f"Update {update} caused error {context.error}")
    
    if update and update.effective_message:
        await update.effective_message.reply_text(
            "❌ Sorry, something went wrong. Please try again or use /start to restart."
        )

def main():
    """Start the bot"""
    print("=" * 50)
    print("🕌 SearchTruth Telegram Bot - Starting...")
    print("=" * 50)
    
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("❌ ERROR: Please update BOT_TOKEN in config.py")
        print("Get your bot token from @BotFather on Telegram")
        print("=" * 50)
        return
    
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # ========== COMMAND HANDLERS ==========
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("search", lambda u, c: quran_search_callback(u, c)))
    application.add_handler(CommandHandler("hadith", lambda u, c: hadith_search_callback(u, c)))
    application.add_handler(CommandHandler("dictionary", lambda u, c: dictionary_search_callback(u, c)))
    
    # ========== CALLBACK QUERY HANDLERS ==========
    # Main menu
    application.add_handler(CallbackQueryHandler(main_menu_callback, pattern=r'^main_'))
    
    # Quran
    application.add_handler(CallbackQueryHandler(quran_search_callback, pattern=r'^quran_search$'))
    application.add_handler(CallbackQueryHandler(quran_translation_callback, pattern=r'^qtrans_'))
    
    # Hadith
    application.add_handler(CallbackQueryHandler(hadith_search_callback, pattern=r'^hadith_search$'))
    application.add_handler(CallbackQueryHandler(hadith_collection_callback, pattern=r'^hcollection_'))
    
    # Prayer
    application.add_handler(CallbackQueryHandler(prayer_country_callback, pattern=r'^pcountry_'))
    application.add_handler(CallbackQueryHandler(prayer_country_callback, pattern=r'^prayer_all_countries$'))
    
    # Dictionary
    application.add_handler(CallbackQueryHandler(dictionary_search_callback, pattern=r'^dict_search$'))
    application.add_handler(CallbackQueryHandler(dictionary_search_callback, pattern=r'^dict_search_'))
    application.add_handler(CallbackQueryHandler(dictionary_type_callback, pattern=r'^dicttype_'))
    
    # Other menu callbacks (simplified)
    application.add_handler(CallbackQueryHandler(main_menu_callback, pattern=r'^quran_'))
    application.add_handler(CallbackQueryHandler(main_menu_callback, pattern=r'^hadith_'))
    application.add_handler(CallbackQueryHandler(main_menu_callback, pattern=r'^dict_'))
    
    # ========== MESSAGE HANDLERS ==========
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_quick_search))
    
    # State-specific handlers (with higher priority)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_quran_search), group=1)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_hadith_search), group=2)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_dictionary_search), group=3)
    
    # ========== ERROR HANDLER ==========
    application.add_error_handler(error_handler)
    
    # ========== START BOT ==========
    print("✅ Bot is running...")
    print("Press Ctrl+C to stop")
    print("=" * 50)
    
    application.run_polling()

if __name__ == '__main__':
    main()