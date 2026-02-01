"""
Hadith search handlers for SearchTruth Bot
"""
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from config import HADITH_COLLECTIONS, MAX_HADITH_RESULTS
from search_apis import SearchTruthAPI

logger = logging.getLogger(__name__)
search_api = SearchTruthAPI()

async def hadith_menu(query):
    """Show Hadith search menu"""
    keyboard = [
        [InlineKeyboardButton("🔍 Search Hadith", callback_data='hadith_search')],
        [InlineKeyboardButton("📚 Collections", callback_data='hadith_collections')],
        [InlineKeyboardButton("🔙 Main Menu", callback_data='main_menu')]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "*Hadith Search Menu*\n\n"
        "Search in authentic Hadith collections:",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_markup
    )

async def hadith_search_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start Hadith search process"""
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [
            InlineKeyboardButton("Sahih Bukhari", callback_data='hcollection_1'),
            InlineKeyboardButton("Sahih Muslim", callback_data='hcollection_2')
        ],
        [
            InlineKeyboardButton("Sunan Abu-Dawud", callback_data='hcollection_3'),
            InlineKeyboardButton("Malik's Muwatta", callback_data='hcollection_4')
        ],
        [InlineKeyboardButton("🔙 Back", callback_data='main_hadith')]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "*Select Hadith Collection:*\n\n"
        "Choose which collection to search:",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup