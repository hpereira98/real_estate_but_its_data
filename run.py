from scraping import get_imovirtual_properties
from config import CONFIG

if __name__ == "__main__":
    get_imovirtual_properties(CONFIG.REAL_ESTATE_URL)
