
USD = 65
EUR = 73

CHAT_ID = 'TELEGRAM_CHAT_ID'
TOKEN = 'TELEGRAM_TOKEN'

MIN_RATING = 10

try:
    from settings.local_settings import *
except ImportError:
    print(' - - - - - - - START WITH MAIN SETTINGS - - - - - - - ')
