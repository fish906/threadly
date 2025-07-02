import os
from dotenv import load_dotenv

# Load .env file if present
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "mariadb+mariadbconnector://user:password@localhost:3306/mydb")
LOG_FILE = os.getenv("LOG_FILE", "/opt/projects/webhook_messages/logs/server.log")
