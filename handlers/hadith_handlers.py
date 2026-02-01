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
        reply_markup=reply_markup
    )

async def hadith_collection_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle Hadith collection selection"""
    query = update.callback_query
    await query.answer()
    
    collection_id = query.data.split('_')[1]
    collection_name = HADITH_COLLECTIONS.get(collection_id, {}).get('name', 'Hadith')
    
    context.user_data['hadith_collection'] = collection_id
    
    await query.edit_message_text(
        f"📚 *Search in {collection_name}*\n\n"
        "Please send me the keyword to search for:\n\n"
        "*Examples:*\n"
        "• `prayer`\n"
        "• `charity`\n"
        "• `patience`\n\n"
        "Type your search keyword:",
        parse_mode=ParseMode.MARKDOWN
    )
    
    context.user_data['state'] = 'waiting_hadith_search'

async def handle_hadith_search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Process Hadith search query"""
    if context.user_data.get('state') == 'waiting_hadith_search':
        keyword = update.message.text.strip()
        context.user_data['state'] = None
        
        if not keyword:
            await update.message.reply_text("Please enter a search keyword.")
            return
        
        collection_id = context.user_data.get('hadith_collection', '1')
        collection_name = HADITH_COLLECTIONS.get(collection_id, {}).get('name', 'Hadith')
        
        # Show searching message
        msg = await update.message.reply_text(
            f"🔍 Searching *{collection_name}* for `{keyword}`...\nPlease wait...",
            parse_mode=ParseMode.MARKDOWN
        )
        
        # Perform search
        results = search_api.search_hadith(keyword, collection_id, MAX_HADITH_RESULTS)
        
        # Format results
        if results and "Unable" not in results[0] and "No hadith" not in results[0]:
            response_text = f"*Hadith Search Results*\nCollection: {collection_name}\nKeyword: `{keyword}`\n\n"
            
            for i, result in enumerate(results, 1):
                response_text += f"*{i}.* {result}\n\n"
            
            response_text += "_Search again: /hadith_"
            
            keyboard = [
                [InlineKeyboardButton("🔍 New Search", callback_data='main_hadith')],
                [InlineKeyboardButton("📚 Other Collections", callback_data='hadith_collections')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await msg.edit_text(
                response_text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup,
                disable_web_page_preview=True
            )
        else:
            keyboard = [[InlineKeyboardButton("🔍 Try Again", callback_data='hadith_search')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await msg.edit_text(
                f"*No hadith found for '{keyword}'*\n\n"
                "Try different keywords or try another collection.\n\n"
                "Search again: /hadith",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup
            )