
import json

from app import AI_API_KEY
import uuid
import requests
import uuid


context = ''' 
            "Ты проверяешь домашние задания учеников по программированию.
            Тебе дано задание от учителя и код каждого ученика. 
            Проверь каждого ученика и ответь СТРОГО в формате JSON без лишнего текста.
            Формат: {"results": [{"username": str, "correct": bool,
            "summary": str, "suggestions": str}]}.
            summary — краткое резюме для учителя о работе ученика. 
            suggestions — конкретные рекомендации что можно улучшить. 
            Если код содержит ошибку или не соответствует заданию, correct=false. 
            Ты можешь вызывать функции для получения дополнительной информации о файлах учеников, 
            например чтобы посмотреть другие файлы проекта. 
            Отвечай ТОЛЬКО на русском языке. Верни ТОЛЬКО JSON.
'''

def get_token():
    url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"

    headers = {        
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
        "RqUID": str(uuid.uuid4()),
        "Authorization": f"Basic {AI_API_KEY}",
    }

    data = {
        "scope": "GIGACHAT_API_PERS"
    }

    response = requests.post(url, headers=headers, data=data, verify=False)
    return response.json()["access_token"]


def groq_chat(prompt, code):

    token = get_token()

    url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "GigaChat",
        "messages": [
            {
                "role": "user",
                "content": f"\n{context} + \nЗадание данное ученику: {prompt}" + f"\nКод его решения: {code}"
            }
        ],
        "temperature": 0.6
    }

    response = requests.post(url, headers=headers, json=payload, verify=False)
    return json.loads(response.json()["choices"][0]["message"]["content"])