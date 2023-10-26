import os

# AWS Credentials
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", None)
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", None)
AWS_ENDPOINT_URL = os.getenv("AWS_ENDPOINT_URL" ,"http://localhost:4566")
AWS_BUCKET = os.getenv("AWS_BUCKET", 'real-estate')
AWS_BUCKET_LOCATION = os.getenv("AWS_BUCKET_LOCATION", "data")

# Scraping
REAL_ESTATE_URL = os.getenv("REAL_ESTATE_URL", "https://www.imovirtual.com/comprar/braga/?search%5Bregion_id%5D=3")
REAL_ESTATE_CITY = os.getenv("REAL_ESTATE_CITY", "Braga, Braga")
HTTP_HEADERS = os.getenv("HTTP_HEADERS", {'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148'})
INITIAL_OFFSET = os.getenv("INITIAL_OFFSET", 1)
LAST_PAGE = os.getenv("LAST_PAGE", None)
