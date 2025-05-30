from os import getenv

from dotenv import load_dotenv

load_dotenv()

MONGO_DSN = getenv("MONGO_DSN")
MONGO_DSN_TEST = getenv("MONGO_DSN_TEST")

ENVIRONMENT = getenv("ENVIRONMENT")

ALGORITHM = getenv("ALGORITHM")
SECRET_KEY = getenv("SECURITY_KEY")
SECRET_KEY_USER = getenv("SECRET_KEY_USER")
ACCESS_TOKEN_EXPIRE_MINUTES = getenv("ACCESS_TOKEN_EXPIRE_MINUTES")

