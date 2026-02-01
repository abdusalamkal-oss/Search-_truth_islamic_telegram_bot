"""
Configuration file for SearchTruth Telegram Bot
"""

# Bot Configuration
BOT_TOKEN = "8588204814:AAH61_MWfyjBgTkm1QcXobsxQgGJPI7IfOw"  # Replace with your bot token from @BotFather

# API Configuration
REQUEST_TIMEOUT = 10
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

# Search Limits
MAX_QURAN_RESULTS = 5
MAX_HADITH_RESULTS = 5
MAX_DICTIONARY_RESULTS = 8
MAX_CITIES_DISPLAY = 10

# Quran Chapters (simplified - you can expand this)
QURAN_CHAPTERS = {
    1: {"name": "Al-Fatiha", "verses": 7},
    2: {"name": "Al-Baqara", "verses": 286},
    3: {"name": "Aal-e-Imran", "verses": 200},
    4: {"name": "An-Nisa", "verses": 176},
    5: {"name": "Al-Maeda", "verses": 120},
    6: {"name": "Al-Anaam", "verses": 165},
    7: {"name": "Al-Araf", "verses": 206},
    8: {"name": "Al-Anfal", "verses": 75},
    9: {"name": "At-Taubah", "verses": 129},
    10: {"name": "Yunus", "verses": 109},
    81: {"name": "At-Takwir", "verses": 29},
    85: {"name": "Al-Burooj", "verses": 22},
    90: {"name": "Al-Balad", "verses": 20},
    94: {"name": "Ash-Sharh", "verses": 8},
    100: {"name": "Al-Adiyat", "verses": 11},
    105: {"name": "Al-Fil", "verses": 5},
    110: {"name": "An-Nasr", "verses": 3},
    113: {"name": "Al-Falaq", "verses": 5},
    114: {"name": "An-Nas", "verses": 6}
}

# Translation Options
TRANSLATIONS = {
    "2": {"name": "Yusuf Ali", "lang": "English", "code": "en"},
    "1": {"name": "Arabic", "lang": "Arabic", "code": "ar"},
    "3": {"name": "Shakir", "lang": "English", "code": "en"},
    "4": {"name": "Pickthal", "lang": "English", "code": "en"},
    "6": {"name": "Transliteration", "lang": "Transliteration", "code": "tr"},
    "17": {"name": "Urdu", "lang": "Urdu", "code": "ur"},
    "8": {"name": "French", "lang": "French", "code": "fr"},
    "9": {"name": "Spanish", "lang": "Spanish", "code": "es"},
    "10": {"name": "Indonesian", "lang": "Indonesian", "code": "id"},
    "11": {"name": "Melayu", "lang": "Malay", "code": "ms"},
    "12": {"name": "German", "lang": "German", "code": "de"},
    "19": {"name": "Russian", "lang": "Russian", "code": "ru"}
}

# Hadith Collections
HADITH_COLLECTIONS = {
    "1": {"name": "Sahih Bukhari", "code": "bukhari"},
    "2": {"name": "Sahih Muslim", "code": "muslim"},
    "3": {"name": "Sunan Abu-Dawud", "code": "abudawud"},
    "4": {"name": "Malik's Muwatta", "code": "muwatta"}
}

# Popular Countries for Prayer Times
POPULAR_COUNTRIES = [
    "USA", "UK", "Canada", "Australia", "India", "Pakistan",
    "Saudi Arabia", "UAE", "Egypt", "Turkey", "Malaysia", "Indonesia"
]

# All Countries List
COUNTRIES = [
    "Afghanistan", "Albania", "Algeria", "Andorra", "Angola",
    "Argentina", "Australia", "Austria", "Azerbaijan", "Bahrain",
    "Bangladesh", "Belgium", "Brazil", "Brunei", "Bulgaria",
    "Canada", "China", "Denmark", "Egypt", "Ethiopia",
    "Finland", "France", "Germany", "Ghana", "Greece",
    "India", "Indonesia", "Iran", "Iraq", "Ireland",
    "Italy", "Japan", "Jordan", "Kazakhstan", "Kenya",
    "Kuwait", "Lebanon", "Libya", "Malaysia", "Maldives",
    "Morocco", "Netherlands", "Nigeria", "Norway", "Oman",
    "Pakistan", "Palestine", "Philippines", "Qatar", "Russia",
    "Saudi Arabia", "Singapore", "Somalia", "South Africa", "Spain",
    "Sri Lanka", "Sudan", "Sweden", "Switzerland", "Syria",
    "Tanzania", "Thailand", "Tunisia", "Turkey", "Uganda",
    "Ukraine", "United Arab Emirates", "United Kingdom", "USA", "Uzbekistan",
    "Yemen"
]