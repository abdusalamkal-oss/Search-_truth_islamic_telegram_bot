"""
Prayer times handlers for SearchTruth Bot
"""
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode

from config import MAX_CITIES_DISPLAY

logger = logging.getLogger(__name__)

async def show_cities_for_country(query, prayer_data, country):
    """Show cities for a selected country"""
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

async def prayer_command(update, context):
    """Handle /prayer command"""
    from handlers.main_menu import prayer_menu
    await prayer_menu(update.message)