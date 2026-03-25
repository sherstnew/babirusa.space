from groq import Groq
from app import AI_API_KEY


def groq_chat(prompt, code):

    client = Groq(
        api_key=AI_API_KEY
    )

    completion = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "user",
                "content": prompt + "\nЗадание данное ученику: {img_link}" + "\nКод его решения: {code}" + "\nПроверь работу и напиши 'ошибок нет', если всё верно или распиши ошибки, если они есть"
            }
        ],
        temperature=0.6,
        max_completion_tokens=4096
    )

    return completion.choices[0].message.content