from pymongo import MongoClient
from os import getenv
from dotenv import load_dotenv
from mitmproxy import http, ctx

load_dotenv()

MONGO_DSN = getenv("MONGO_DSN")

client = MongoClient(MONGO_DSN)
db = client.babirusa
    
def request(flow: http.HTTPFlow) -> None:
    userports = db["UserIp"].find()

    SUBDOMAIN_TO_PORT = {}

    for userport in userports:
      SUBDOMAIN_TO_PORT[userport["username"]] = userport["ip"]
      
    
    host = flow.request.pretty_host
    subdomain = host.split(".")[0] 

    if subdomain in SUBDOMAIN_TO_PORT:
        new_port = SUBDOMAIN_TO_PORT[subdomain]
        flow.request.headers["Host"] = f"{subdomain}.babirusa.space"
        # Дополнительно можно передать X-Forwarded-*
        flow.request.headers["X-Forwarded-Host"] = f"{subdomain}.babirusa.space"
        flow.request.headers["X-Forwarded-Proto"] = "https"
        flow.websocket_proxy = True
        flow.request.host = new_port
        flow.request.port = 8080
        ctx.log.info(f"Перенаправляем {host} → {new_port}:8080")
    else:
        if subdomain == "api":
          flow.request.host = "127.0.0.1"
          flow.request.port = 999
        else:  
          flow.request.host = "127.0.0.1"
          flow.request.port = 111
          ctx.log.warn(f"Неизвестный поддомен: {host}")

# Запуск: mitmweb -s subdomain_proxy.py --mode reverse:http://127.0.0.1/