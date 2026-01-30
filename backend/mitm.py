from pymongo import MongoClient
from os import getenv
from dotenv import load_dotenv
from mitmproxy import http, ctx
import logging

load_dotenv()

logging.basicConfig(level=logging.ERROR)

MONGO_DSN = getenv("MONGO_DSN")
MITM_MODE = getenv("MITM_MODE")
IP_ADDRESS = getenv("IP_ADDRESS")

# Создаем клиент один раз
client = MongoClient(MONGO_DSN, serverSelectionTimeoutMS=2000)
db = client.get_default_database()

def request(flow: http.HTTPFlow) -> None:
    host = flow.request.pretty_host

    if "babirusa.space" not in host:
        flow.kill()
        return

    try:
        userports = list(db["UserIp"].find({}, {"username": 1, "ip": 1}))
        SUBDOMAIN_TO_PORT = {u["username"]: u["ip"] for u in userports}
    except Exception as e:
        ctx.log.error(f"MongoDB Error: {e}")
        flow.response = http.Response.make(503, b"Database Error")
        return

    if MITM_MODE == "PATH":
        parts = flow.request.path.split("/")
        path = parts[1] if len(parts) > 1 else ""
        
        if path in SUBDOMAIN_TO_PORT:
            new_ip = SUBDOMAIN_TO_PORT[path]
            flow.request.headers["Host"] = f"babirusa.space"
            flow.request.headers["X-Forwarded-Host"] = f"babirusa.space/{path}"
            flow.request.headers["X-Forwarded-Proto"] = "https"
            flow.websocket_proxy = True
            flow.request.host = new_ip
            flow.request.port = 8080
        else:
            flow.request.host = IP_ADDRESS
            flow.request.port = 5000 if path == "api" else 1000
    else:
        subdomain = host.split(".")[0]
        if subdomain in SUBDOMAIN_TO_PORT:
            new_ip = SUBDOMAIN_TO_PORT[subdomain]
            flow.request.headers["Host"] = f"{subdomain}.babirusa.space"
            flow.request.headers["X-Forwarded-Host"] = f"{subdomain}.babirusa.space"
            flow.request.headers["X-Forwarded-Proto"] = "https"
            flow.websocket_proxy = True
            flow.request.host = new_ip
            flow.request.port = 8080
        else:
            flow.request.host = IP_ADDRESS
            flow.request.port = 5000 if subdomain == "api" else 1000