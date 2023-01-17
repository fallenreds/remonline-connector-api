import os
from dotenv import load_dotenv
load_dotenv()

REMONLINE_API_KEY_PROD = os.getenv('API_KEY_PROD')
REMONLINE_API_KEY_TEST = os.getenv('API_KEY_TEST')