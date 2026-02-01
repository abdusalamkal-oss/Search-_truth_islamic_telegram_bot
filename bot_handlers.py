"""
Telegram bot handlers for SearchTruth Bot
"""
import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from config import (
    QURAN_CHAPTERS, TRANSLATIONS, HADITH_COLLECTIONS,
    POPULAR_COUNTRIES, COUNTRIES, MAX_QURAN_RESULTS,
    MAX_HADITH_RESULTS, MAX_DICTIONARY_RESULTS, MAX_CITIES_DISPLAY
)
from search_apis import SearchTruthAPI

logger = logging.getLogger(__name__)
search_api = SearchTruthAPI()

# ========== HELPER FUNCTIONS ==========

def get_hijri_date() -> str:
    """Get current Hijri date (simplified approximation)"""
    try:
        today = datetime.now()
        hijri_months = [
            "Muharram", "Safar", "Rabi' al-Awwal", "Rabi' al-Thani",
            "Jumada al-Awwal", "Jumada al-Thani", "Rajab", "Sha'ban",
            "Ramadan", "Shawwal", "Dhu al-Qi'dah", "Dhu al-Hijjah"
        ]
        
        # Simple approximation (not astronomically accurate)
        hijri_year = 1445 + (today.year - 2023)
        hijri_month = hijri_months[today.month - 1]
        hijri_day = today.day % 29 or 1  # Islamic months are 29-30 days
        
        return f"{hijri_day} {hijri_month} {hijri_year} AH"
    except Exception as e:
        logger.error(f"Hijri date error: {e}")
        return "Unable to fetch Hijri date"

# ========== MAIN MENU HANDLERS ==========

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command"""
    user = update.effective_user
    
    welcome_text = f"""
🕌 *Assalamu Alaikum {user.first_name}!*

Welcome to *SearchTruth Bot* – Your Islamic Knowledge Companion 📖

*Available Features:*
1. 🔍 *Quran Search* – Search verses in multiple translations
2. 📚 *Hadith Search* – Search in major Hadith collections
3. 🕌 *Prayer Times* – Get prayer times worldwide
4. 📖 *Dictionary* – English-Arabic dictionary
5. 📅 *Hijri Date* – Current Islamic date

*Quick Commands:*
/search – Open search menu
/prayer – Get prayer times
/hadith – Search Hadith
/dictionary – English-Arabic dictionary
/hijri – Current Hijri date
/help – Show all commands

Made with ❤️ using SearchTruth.com APIs
    """
    
    keyboard = [
        [InlineKeyboardButton("🔍 Search Quran", callback_data='main_quran')],
        [InlineKeyboardButton("📚 Search Hadith", callback_data='main_hadith')],
        [InlineKeyboardButton("🕌 Prayer Times", callback_data='main_prayer')],
        [InlineKeyboardButton("📖 Dictionary", callback_data='main_dict')],
        [InlineKeyboardButton("📅 Hijri Date", callback_data='main_hijri')],
        [InlineKeyboardButton("ℹ️ Help / Commands", callback_data='main_help')]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        welcome_text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_markup
    )

async def main_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle main menu callbacks"""
    query = update.callback_query
    await query.answer()
    
    callback_data = query.data
    
    if callback_data == 'main_quran':
        await quran_menu(query)
    elif callback_data == 'main_hadith':
        await hadith_menu(query)
    elif callback_data == 'main_prayer':
        await prayer_menu(query)
    elif callback_data == 'main_dict':
        await dictionary_menu(query)
    elif callback_data == 'main_hijri':
        await hijri_date_command(query)
    elif callback_data == 'main_help':
        await help_command(query)

# ========== QURAN HANDLERS ==========

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

# ========== HADITH HANDLERS ==========

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

# ========== PRAYER TIMES HANDLERS ==========

async def prayer_menu(query):
    """Show Prayer Times menu"""
    keyboard = []
    
    # Add popular countries in rows of 2
    for i in range(0, len(POPULAR_COUNTRIES), 2):
        row = []
        if i < len(POPULAR_COUNTRIES):
            row.append(InlineKeyboardButton(POPULAR_COUNTRIES[i], callback_data=f'pcountry_{POPULAR_COUNTRIES[i]}'))
        if i + 1 < len(POPULAR_COUNTRIES):
            row.append(InlineKeyboardButton(POPULAR_COUNTRIES[i+1], callback_data=f'pcountry_{POPULAR_COUNTRIES[i+1]}'))
        keyboard.append(row)
    
    keyboard.append([InlineKeyboardButton("🌍 All Countries", callback_data='prayer_all_countries')])
    keyboard.append([InlineKeyboardButton("🔙 Main Menu", callback_data='main_menu')])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "*Prayer Times Worldwide*\n\n"
        "Select a country to get prayer times:\n\n"
        "_Note: You'll need to select a city after choosing country_",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_markup
    )

async def prayer_country_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle country selection for prayer times"""
    query = update.callback_query
    await query.answer()
    
    if query.data == 'prayer_all_countries':
        await show_all_countries(query)
        return
    
    country = query.data.replace('pcountry_', '')
    
    # Get prayer times/cities for this country
    prayer_data = search_api.get_prayer_cities(country)
    
    if 'error' in prayer_data:
        await query.edit_message_text(
            f"*Error:* {prayer_data['error']}\n\n"
            f"{prayer_data.get('suggestion', 'Please try another country.')}",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    
    if 'available_cities' in prayer_data:
        # Show cities for this country
        cities = prayer_data['available_cities']
        
        keyboard = []
        for i in range(0, min(len(cities), MAX_CITIES_DISPLAY), 2):
            row = []
            if i < len(cities):
                row.append(InlineKeyboardButton(cities[i], callback_data=f'pcity_{country}_{cities[i]}'))
            if i + 1 < len(cities):
                row.append(InlineKeyboardButton(cities[i+1], callback_data=f'pcity_{country}_{cities[i+1]}'))
            keyboard.append(row)
        
        keyboard.append([InlineKeyboardButton("🔙 Back to Countries", callback_data='main_prayer')])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"*Prayer Times - {country}*\n\n"
            f"Found {prayer_data['total_cities']} cities.\n"
            "Select a city:\n\n"
            f"_Showing first {MAX_CITIES_DISPLAY} cities. For more cities, visit SearchTruth.com_",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )

async def show_all_countries(query):
    """Show all countries for prayer times"""
    countries_text = '\n'.join([f"• {c}" for c in COUNTRIES[:25]])
    
    keyboard = [[InlineKeyboardButton("🔙 Back", callback_data='main_prayer')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "*All Available Countries*\n\n"
        f"Total: {len(COUNTRIES)} countries\n\n"
        f"{countries_text}\n\n"
        "_...and many more_\n\n"
        "To get prayer t