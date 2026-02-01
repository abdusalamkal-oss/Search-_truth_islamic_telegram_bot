"""
Dictionary handlers for SearchTruth Bot
"""
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from config import MAX_DICTIONARY_RESULTS
from search_apis import SearchTruthAPI

logger = logging.getLogger(__name__)
search_api = SearchTruthAPI()

async def dictionary_menu(query):
    """Show Dictionary menu"""
    keyboard = [
        [InlineKeyboardButton("🔍 Search Dictionary", callback_data='dict_search')],
        [InlineKeyboardButton("🔤 A-Z Index", callback_data='dict_az')],
        [InlineKeyboardButton("🔙 Main Menu", callback_data='main_menu')]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "*English-Arabic Dictionary*\n\n"
        "Search for word meanings and translations:",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_markup
    )

async def dictionary_search_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start dictionary search"""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "*Dictionary Search*\n\n"
        "Enter an English word to find its Arabic meaning:\n\n"
        "*Examples:*\n"
        "• `book`\n"
        "• `prayer`\n"
        "• `Quran`\n\n"
        "Type your word:",
        parse_mode=ParseMode.MARKDOWN
    )
    
    context.user_data['state'] = 'waiting_dict_search'

async def handle_dictionary_search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Process dictionary search"""
    if context.user_data.get('state') == 'waiting_dict_search':
        word = update.message.text.strip()
        context.user_data['state'] = None
        
        if not word:
            await update.message.reply_text("Please enter a word to search.")
            return
        
        # Ask for search type
        keyboard = [
            [
                InlineKeyboardButton("Exact Match", callback_data=f'dicttype_1_{word}'),
                InlineKeyboardButton("Partial Match", callback_data=f'dicttype_2_{word}')
            ],
            [InlineKeyboardButton("🔙 Back", callback_data='main_dict')]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"*Search for:* `{word}`\n\n"
            "Select search type:",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )

async def dictionary_type_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle dictionary search type"""
    query = update.callback_query
    await query.answer()
    
    parts = query.data.split('_')
    search_type = parts[1]
    word = parts[2]
    
    search_type_text = "Exact Word" if search_type == "1" else "Sub Word"
    
    await query.edit_message_text(
        f"🔍 Searching dictionary for *{word}*...\n"
        f"Mode: {search_type_text}\n"
        "Please wait...",
        parse_mode=ParseMode.MARKDOWN
    )
    
    # Perform search
    results = search_api.search_dictionary(word, search_type, MAX_DICTIONARY_RESULTS)
    
    # Format results
    if results and "Unable" not in results[0] and "No dictionary" not in results[0]:
        response_text = f"*Dictionary Results for '{word}'*\n\n"
        
        for i, result in enumerate(results, 1):
            response_text += f"*{i}.* {result}\n\n"
        
        response_text += "_Search again: /dictionary_"
        
        keyboard = [
            [InlineKeyboardButton("🔍 New Search", callback_data='dict_search')],
            [InlineKeyboardButton("🔤 A-Z Index", callback_data='dict_az')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            response_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup,
            disable_web_page_preview=True
        )
    else:
        keyboard = [[InlineKeyboardButton("🔍 Try Again", callback_data='dict_search')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"*No dictionary entries found for '{word}'*\n\n"
            "Try:\n"
            "• Different spelling\n"
            "• Root words\n"
            "• Simpler terms\n\n"
            "Search again: /dictionary",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )