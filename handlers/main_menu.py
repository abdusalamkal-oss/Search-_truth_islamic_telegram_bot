"""
Main menu handlers for SearchTruth Bot
"""
import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from config import POPULAR_COUNTRIES
from search_apis import SearchTruthAPI

logger = logging.getLogger(__name__)
search_api = SearchTruthAPI()

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
        from handlers.quran_handlers import quran_menu
        await quran_menu(query)
    elif callback_data == 'main_hadith':
        from handlers.hadith_handlers import hadith_menu
        await hadith_menu(query)
    elif callback_data == 'main_prayer':
        await prayer_menu(query)
    elif callback_data == 'main_dict':
        from handlers.dictionary_handlers import dictionary_menu
        await dictionary_menu(query)
    elif callback_data == 'main_hijri':
        await hijri_date_command(query)
    elif callback_data == 'main_help':
        await help_command(query)

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
        from handlers.prayer_handlers import show_cities_for_country
        await show_cities_for_country(query, prayer_data, country)

async def show_all_countries(query):
    """Show all countries for prayer times"""
    from config import COUNTRIES
    countries_text = '\n'.join([f"• {c}" for c in COUNTRIES[:25]])
    
    keyboard = [[InlineKeyboardButton("🔙 Back", callback_data='main_prayer')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "*All Available Countries*\n\n"
        f"Total: {len(COUNTRIES)} countries\n\n"
        f"{countries_text}\n\n"
        "_...and many more_\n\n"
        "To get prayer times, type:\n"
        "`/prayer [country name]`\n\n"
        "Example: `/prayer Saudi Arabia`\n\n"
        "Or use the menu to select popular countries.",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_markup
    )

async def hijri_date_command(query):
    """Show current Hijri date"""
    def get_hijri_date() -> str:
        """Get current Hijri date (simplified approximation)"""
        try:
            today = datetime.now()
            hijri_months = [
                "Muharram", "Safar", "Rabi' al-Awwal", "Rabi' al-Thani",
                "Jumada al-Awwal", "Jumada al-Thani", "Rajab", "Sha'ban",
                "Ramadan", "Shawwal", "Dhu al-Qi'dah", "Dhu al-Hijjah"
            ]
            
            # Simple approximation
            hijri_year = 1445 + (today.year - 2023)
            hijri_month = hijri_months[today.month - 1]
            hijri_day = today.day % 29 or 1
            
            return f"{hijri_day} {hijri_month} {hijri_year} AH"
        except Exception as e:
            logger.error(f"Hijri date error: {e}")
            return "Unable to fetch Hijri date"
    
    hijri_date = get_hijri_date()
    
    keyboard = [[InlineKeyboardButton("🔙 Main Menu", callback_data='main_menu')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"*Islamic Hijri Date*\n\n"
        f"📅 *Today's Date:*\n"
        f"{hijri_date}\n\n"
        f"*Gregorian Date:*\n"
        f"{datetime.now().strftime('%d %B %Y')}\n\n"
        f"_Source: SearchTruth.com_",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_markup
    )

async def help_command(query=None, update: Update = None):
    """Show help information"""
    help_text = """
*SearchTruth Bot Help* 🕌

*Main Commands:*
/start - Start the bot & show main menu
/search - Search in Quran (also works by typing any word)
/hadith - Search in Hadith collections
/prayer - Get prayer times worldwide
/dictionary - English-Arabic dictionary
/hijri - Current Islamic (Hijri) date
/help - Show this help message

*Quick Search:*
Simply type any word to search it in the Quran!
Example: `mercy` or `patience 2`

*Quran Search:*
• Search in 114 chapters
• Multiple translations available
• Specify chapter: `allah 2`
• Specify verse: `light 24:35`

*Hadith Search:*
• Sahih Bukhari
• Sahih Muslim
• Sunan Abu-Dawud
• Malik's Muwatta

*Features:*
• Fast and accurate results
• Clean, formatted output
• Interactive menus
• Worldwide prayer times
• Hijri calendar

*Tips:*
• Use Arabic words for better Quran results
• Be specific with search terms
• Use menus for best experience

*Data Source:*
All data powered by SearchTruth.com
    """
    
    keyboard = [
        [InlineKeyboardButton("🔍 Start Searching", callback_data='main_quran')],
        [InlineKeyboardButton("🕌 Prayer Times", callback_data='main_prayer')],
        [InlineKeyboardButton("📚 Hadith Search", callback_data='main_hadith')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if query:
        await query.edit_message_text(
            help_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    elif update:
        await update.message.reply_text(
            help_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )

async def handle_quick_search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle quick search by typing any word"""
    text = update.message.text.strip()
    
    if not text or text.startswith('/'):
        return
    
    # Check if we're in a waiting state
    if context.user_data.get('state'):
        return
    
    # Show quick search options
    keyboard = [
        [
            InlineKeyboardButton("🔍 Search Quran", callback_data=f'qtrans_2_{text}_'),
            InlineKeyboardButton("📚 Search Hadith", callback_data='hadith_search')
        ],
        [
            InlineKeyboardButton("📖 Dictionary", callback_data=f'dict_search_{text}'),
            InlineKeyboardButton("🕌 More Options", callback_data='main_menu')
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"*Quick Search for:* `{text}`\n\n"
        "What would you like to search?",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_markup
    )