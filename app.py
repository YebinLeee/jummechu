from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
import os

from routes import router

# Load environment variables
load_dotenv()

# Create FastAPI instance
app = FastAPI()

# Set up templates
templates = Jinja2Templates(directory="templates")

# Include routers
app.include_router(router)

# Load configuration from environment variables
NAVER_CLIENT_ID = os.getenv('NAVER_CLIENT_ID')
NAVER_CLIENT_SECRET = os.getenv('NAVER_CLIENT_SECRET')
CLOVA_HOST = os.getenv('CLOVA_HOST')
CLOVA_API_KEY = os.getenv('CLOVA_API_KEY')
CLOVA_API_KEY_PRIMARY = os.getenv('CLOVA_API_KEY_PRIMARY')
CLOVA_REQUEST_ID = os.getenv('CLOVA_REQUEST_ID')