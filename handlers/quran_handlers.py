"""
Quran search handlers for SearchTruth Bot
"""
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from config import QURAN_CHAPTERS, TRANSLATIONS, MAX_QURAN_RESULTS
from search_apis import SearchTruthAPI

logger = logging.getLogger(__name__)
search_api = SearchTruthAPI()

async def quran_menu(query):
    """Show Quran search menu"""
    keyboard = [
        [InlineKeyboardButton("🔍 Search by Keyword", callback_data='quran_search')],
        [InlineKeyboardButton("📚 Browse Chapters", callback_data='quran_chapters')],
        [InlineKeyboardButton("🔄 Random Verse", callback_data='quran_random')],
        [InlineKeyboardButton("🔙 Main Menu", callback_data='main_menu')]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "*Quran Search Menu*\n\n"
        "Choose an option:",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_markup
    )

async def quran_search_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start Quran search process"""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "🔍 *Quran Search*\n\n"
        "Please send me the keyword you want to search for.\n\n"
        "*Examples:*\n"
        "• `mercy` – Search in all chapters\n"
        "• `patience 2` – Search in chapter 2\n"
        "• `Allah 1:1` – Search in chapter 1, verse 1\n\n"
        "Type your search now:",
        parse_mode=ParseMode.MARKDOWN
    )
    
    context.user_data['state'] = 'waiting_quran_search'

async def handle_quran_search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Process Quran search query"""
    if context.user_data.get('state') == 'waiting_quran_search':
        search_text = update.message.text.strip()
        context.user_data['state'] = None
        
        if not search_text:
            await update.message.reply_text("Please enter a search keyword.")
            return
        
        # Parse search text
        parts = search_text.split()
        keyword = parts[0]
        chapter = ""
        
        if len(parts) > 1:
            # Check if second part is a chapter number
            if parts[1].isdigit():
                chapter = parts[1]
            elif ':' in parts[1]:
                # Format like "1:1"
                chapter = parts[1].split(':')[0]
        
        # Ask for translation
        keyboard = [
            [
                InlineKeyboardButton("🇬🇧 Yusuf Ali", callback_data=f'qtrans_2_{keyword}_{chapter}'),
                InlineKeyboardButton("🇸🇦 Arabic", callback_data=f'qtrans_1_{keyword}_{chapter}')
            ],
            [
                InlineKeyboardButton("🇵🇰 Urdu", callback_data=f'qtrans_17_{keyword}_{chapter}'),
                InlineKeyboardButton("🇫🇷 French", callback_data=f'qtrans_8_{keyword}_{chapter}')
            ],
            [
                InlineKeyboardButton("🇪🇸 Spanish", callback_data=f'qtrans_9_{keyword}_{chapter}'),
                InlineKeyboardButton("More...", callback_data=f'qtrans_more_{keyword}_{chapter}')
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        chapter_text = f" in chapter {chapter}" if chapter else ""
        await update.message.reply_text(
            f"🔍 *Searching for:* `{keyword}`{chapter_text}\n\n"
            "Select translation:",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )

async def quran_translation_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle Quran translation selection and perform search"""
    query = update.callback_query
    await query.answer()
    
    parts = query.data.split('_')
    
    if parts[1] == 'more':
        # Show more translations
        keyword = parts[2]
        chapter = parts[3] if len(parts) > 3 else ""
        
        keyboard = [
            [
                InlineKeyboardButton("Shakir (EN)", callback_data=f'qtrans_3_{keyword}_{chapter}'),
                InlineKeyboardButton("Pickthal (EN)", callback_data=f'qtrans_4_{keyword}_{chapter}')
            ],
            [
                InlineKeyboardButton("Transliteration", callback_data=f'qtrans_6_{keyword}_{chapter}'),
                InlineKeyboardButton("German", callback_data=f'qtrans_12_{keyword}_{chapter}')
            ],
            [
                InlineKeyboardButton("🔙 Back", callback_data=f'qtrans_back_{keyword}_{chapter}')
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "More translation options:",
            reply_markup=reply_markup
        )
        return
    
    if parts[1] == 'back':
        # Go back to main translation menu
        keyword = parts[2]
        chapter = parts[3] if len(parts) > 3 else ""
        
        keyboard = [
            [
                InlineKeyboardButton("🇬🇧 Yusuf Ali", callback_data=f'qtrans_2_{keyword}_{chapter}'),
                InlineKeyboardButton("🇸🇦 Arabic", callback_data=f'qtrans_1_{keyword}_{chapter}')
            ],
            [
                InlineKeyboardButton("🇵🇰 Urdu", callback_data=f'qtrans_17_{keyword}_{chapter}'),
                InlineKeyboardButton("🇫🇷 French", callback_data=f'qtrans_8_{keyword}_{chapter}')
            ],
            [
                InlineKeyboardButton("🇪🇸 Spanish", callback_data=f'qtrans_9_{keyword}_{chapter}'),
                InlineKeyboardButton("More...", callback_data=f'qtrans_more_{keyword}_{chapter}')
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        chapter_text = f" in chapter {chapter}" if chapter else ""
        await query.edit_message_text(
            f"🔍 *Searching for:* `{keyword}`{chapter_text}\n\n"
            "Select translation:",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
        return
    
    # Normal translation selection
    translator = parts[1]
    keyword = parts[2]
    chapter = parts[3] if len(parts) > 3 else ""
    
    # Show searching message
    translation_name = TRANSLATIONS.get(translator, {}).get('name', 'Unknown')
    await query.edit_message_text(
        f"🔍 Searching Quran for *{keyword}*...\n"
        f"Translation: {translation_name}\n"
        "Please wait...",
        parse_mode=ParseMode.MARKDOWN
    )
    
    # Perform search
    results = search_api.search_quran(keyword, chapter, translator, MAX_QURAN_RESULTS)
    
    # Format results
    if chapter and chapter.isdigit() and int(chapter) in QURAN_CHAPTERS:
        chapter_name = QURAN_CHAPTERS[int(chapter)]['name']
        header = f"*Results for '{keyword}' in {chapter_name}*\n"
    else:
        header = f"*Results for '{keyword}'*\n"
    
    response_text = f"{header}Translation: {translation_name}\n\n"
    
    if results and "Unable" not in results[0] and "No Quran" not in results[0]:
        for i, result in enumerate(results, 1):
            clean_result = result.replace('[', '*[').replace(']', ']*')
            response_text += f"*{i}.* {clean_result}\n\n"
        
        if len(results) == MAX_QURAN_RESULTS:
            response_text += f"_Showing {MAX_QURAN_RESULTS} results_\n\n"
        
        response_text += "✨ *Search again:* /search"
        
        keyboard = [
            [InlineKeyboardButton("🔍 New Search", callback_data='main_quran')],
            [InlineKeyboardButton("📚 Browse Chapters", callback_data='quran_chapters')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            response_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup,
            disable_web_page_preview=True
        )
    else:
        keyboard = [[InlineKeyboardButton("🔍 Try Again", callback_data='quran_search')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"*No Quran verses found for '{keyword}'*\n\n"
            "Suggestions:\n"
            "• Try different keywords\n"
            "• Use Arabic words\n"
            "• Try broader search terms\n\n"
            "Search again: /search",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )