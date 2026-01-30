from pymongo import MongoClient
from os import getenv
from dotenv import load_dotenv
from mitmproxy import http, ctx

load_dotenv()

MONGO_DSN = getenv("MONGO_DSN")
MITM_MODE = getenv("MITM_MODE")
IP_ADDRESS = getenv("IP_ADDRESS")

client = MongoClient(MONGO_DSN)
db = client.get_default_database()

def request(flow: http.HTTPFlow) -> None:
    userports = db["UserIp"].find()

    SUBDOMAIN_TO_PORT = {}

    for userport in userports:
        SUBDOMAIN_TO_PORT[userport["username"]] = userport["ip"]

    host = flow.request.pretty_host

    if "babirusa.space" not in host:
        return

    if MITM_MODE == "PATH":
        path = host.split("/")[1]
        if path in SUBDOMAIN_TO_PORT:
            new_port = SUBDOMAIN_TO_PORT[subdomain]
            flow.request.headers["Host"] = f"babirusa.space/{path}"
            flow.request.headers["X-Forwarded-Host"] = f"babirusa.space/{path}"
            flow.request.headers["X-Forwarded-Proto"] = "https"
            flow.websocket_proxy = True
            flow.request.host = new_port
            flow.request.port = 8080
        else:
            if path == "api":
                flow.request.host = IP_ADDRESS
                flow.request.port = 5000
            else:
                flow.request.host = IP_ADDRESS
                flow.request.port = 1000
    else:
        subdomain = host.split(".")[0]
        if subdomain in SUBDOMAIN_TO_PORT:
            new_port = SUBDOMAIN_TO_PORT[subdomain]
            flow.request.headers["Host"] = f"{subdomain}.babirusa.space"
            flow.request.headers["X-Forwarded-Host"] = f"{subdomain}.babirusa.space"
            flow.request.headers["X-Forwarded-Proto"] = "https"
            flow.websocket_proxy = True
            flow.request.host = new_port
            flow.request.port = 8080
        else:
            if subdomain == "api":
                flow.request.host = IP_ADDRESS
                flow.request.port = 5000
            else:
                flow.request.host = IP_ADDRESS
                flow.request.port = 1000
