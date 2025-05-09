from pymongo import MongoClient
from os import getenv
from dotenv import load_dotenv
from mitmproxy import http, ctx

load_dotenv()

MONGO_DSN = getenv("MONGO_DSN")

client = MongoClient(MONGO_DSN)
db = client.babirusa
userports = db["UserPort"].find()

SUBDOMAIN_TO_PORT = {}

for userport in userports:
  SUBDOMAIN_TO_PORT[userport["username"]] = userport["port"]
  
print(SUBDOMAIN_TO_PORT)
    
def request(flow: http.HTTPFlow) -> None:
    host = flow.request.pretty_host  # Получаем поддомен (sub1.example.com)
    subdomain = host.split(".")[0]   # Извлекаем "sub1"

    if subdomain in SUBDOMAIN_TO_PORT:
        new_port = SUBDOMAIN_TO_PORT[subdomain]
        flow.websocket_proxy = True
        flow.request.host = "127.0.0.1"
        flow.request.port = new_port
        flow.request.headers["Connection"] = "upgrade"
        
        flow.request.headers["Accept-Encoding"] = "gzip"
        
        flow.request.headers["Host"] = flow.request.host
        ctx.log.info(f"Перенаправляем {host} → 127.0.0.1:{new_port}")
    else:
        if subdomain == "api":
          flow.request.host = "127.0.0.1"
          flow.request.port = 999
        else:  
          flow.request.host = "127.0.0.1"
          flow.request.port = 111
          ctx.log.warn(f"Неизвестный поддомен: {host}")

# Запуск: mitmweb -s subdomain_proxy.py --mode reverse:http://127.0.0.1/