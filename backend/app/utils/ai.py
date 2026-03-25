from groq import Groq
from app import AI_API_KEY

context = ''' 
            "Ты проверяешь домашние задания учеников по программированию.
            Тебе дано задание от учителя и код каждого ученика. 
            Проверь каждого ученика и ответь СТРОГО в формате JSON без лишнего текста.
            Формат: {"results": [{"username": str, "correct": bool, "score": int (0-10),
            "summary": str, "suggestions": str}]}.
            summary — краткое резюме для учителя о работе ученика. 
            suggestions — конкретные рекомендации что можно улучшить. 
            Если код содержит ошибку или не соответствует заданию, correct=false. 
            Ты можешь вызывать функции для получения дополнительной информации о файлах учеников, 
            например чтобы посмотреть другие файлы проекта. 
            Отвечай ТОЛЬКО на русском языке. Верни ТОЛЬКО JSON.
'''


def groq_chat(prompt, code):

    client = Groq(
        api_key=AI_API_KEY
    )

    completion = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "user",
                "content": f"\n{context} + \nЗадание данное ученику: {prompt}" + "\nКод его решения: {code}"
            }
        ],
        temperature=0.6,
        max_completion_tokens=4096
    )

    return completion.choices[0].message.content