import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

SECRET_KEY = os.getenv("SECRET_KEY", "changeme")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Flow.cl Payment Gateway
FLOW_API_KEY = os.getenv("FLOW_API_KEY", "")
FLOW_SECRET_KEY = os.getenv("FLOW_SECRET_KEY", "")
FLOW_API_URL = os.getenv("FLOW_API_URL", "https://sandbox.flow.cl/api")
FLOW_URL_RETURN = os.getenv(
    "FLOW_URL_RETURN",
    "https://jm-gyms.vercel.app/cliente/pago/retorno",
)
FLOW_URL_CONFIRMATION = os.getenv(
    "FLOW_URL_CONFIRMATION",
    "https://jm-gym.vercel.app/api/payments/flow/confirmation",
)