import json
import os

from app.data.schemas import PupilReview
from app.utils.file_manager import BABIRUSA_HOME, FileManager
from app.utils.gigachat import gigachat_client

TOOL_DEFINITIONS = [
    {
        "name": "list_files",
        "description": "Получить список всех файлов в проекте ученика",
        "parameters": {
            "type": "object",
            "properties": {
                "username": {
                    "type": "string",
                    "description": "Никнейм ученика",
                }
            },
            "required": ["username"],
        },
    },
    {
        "name": "read_file",
        "description": "Прочитать содержимое конкретного файла из проекта ученика",
        "parameters": {
            "type": "object",
            "properties": {
                "username": {
                    "type": "string",
                    "description": "Никнейм ученика",
                },
                "path": {
                    "type": "string",
                    "description": "Относительный путь к файлу внутри проекта",
                },
            },
            "required": ["username", "path"],
        },
    },
    {
        "name": "search_in_files",
        "description": "Поиск текста во всех файлах проекта ученика",
        "parameters": {
            "type": "object",
            "properties": {
                "username": {
                    "type": "string",
                    "description": "Никнейм ученика",
                },
                "text": {
                    "type": "string",
                    "description": "Текст или паттерн для поиска",
                },
            },
            "required": ["username", "text"],
        },
    },
]


def _execute_tool(name: str, arguments: dict, allowed_usernames: list[str]) -> str:
    username = arguments.get("username", "")
    if username not in allowed_usernames:
        return json.dumps(
            {"error": f"Ученик '{username}' не в списке проверки."},
            ensure_ascii=False,
        )

    prj_path = os.path.normpath(os.path.join(BABIRUSA_HOME, f"user-{username}-prj"))
    if not os.path.isdir(prj_path):
        return json.dumps(
            {"error": f"Директория проекта для '{username}' не найдена."},
            ensure_ascii=False,
        )

    fm = FileManager(username=username)

    try:
        if name == "list_files":
            files = fm.list_all_files()
            return json.dumps(
                [
                    {"name": f.name, "path": f.relative_path, "size": f.size}
                    for f in files
                ],
                ensure_ascii=False,
            )

        elif name == "read_file":
            path = arguments.get("path", "")
            content = fm.read_file(path)
            return json.dumps(
                {
                    "path": content.relative_path,
                    "content": content.content,
                    "size": content.size,
                },
                ensure_ascii=False,
            )

        elif name == "search_in_files":
            text = arguments.get("text", "")
            results = fm.search_in_files(text)
            return json.dumps(
                [
                    {
                        "path": r.relative_path,
                        "line": r.line_number,
                        "content": r.line_content,
                    }
                    for r in results
                ],
                ensure_ascii=False,
            )

        return json.dumps({"error": f"Неизвестная функция: {name}"}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


def _gather_pupil_codes(usernames: list[str], file_pattern: str) -> dict[str, str]:
    codes: dict[str, str] = {}
    for username in usernames:
        prj_path = os.path.normpath(os.path.join(BABIRUSA_HOME, f"user-{username}-prj"))
        if not os.path.isdir(prj_path):
            codes[username] = "[ОШИБКА: директория проекта не найдена]"
            continue

        fm = FileManager(username=username)
        found = fm.find_by_name(file_pattern)
        if not found:
            codes[username] = f"[ОШИБКА: файл по шаблону '{file_pattern}' не найден]"
            continue

        try:
            content = fm.read_file(found[0].relative_path)
            codes[username] = content.content
        except Exception as e:
            codes[username] = f"[ОШИБКА: {e}]"

    return codes


def _build_messages(
    prompt: str, file_pattern: str, pupil_codes: dict[str, str]
) -> list[dict]:
    pupils_section = ""
    for username, code in pupil_codes.items():
        pupils_section += f"\n--- УЧЕНИК: {username} ---\n```\n{code}\n```\n"

    sys_msg = {
        "role": "system",
        "content": (
            "Ты проверяешь домашние задания учеников по программированию. "
            "Тебе дано задание от учителя и код каждого ученика. "
            "Проверь каждого ученика и ответь СТРОГО в формате JSON без лишнего текста. "
            'Формат: {"results": [{"username": str, "correct": bool, "score": int (0-10), '
            '"summary": str, "suggestions": str}]}. '
            "summary — краткое резюме для учителя о работе ученика. "
            "suggestions — конкретные рекомендации что можно улучшить. "
            "Если код содержит ошибку или не соответствует заданию, correct=false. "
            "Ты можешь вызывать функции для получения дополнительной информации о файлах учеников, "
            "например чтобы посмотреть другие файлы проекта. "
            "Отвечай ТОЛЬКО на русском языке. Верни ТОЛЬКО JSON."
        ),
    }

    user_msg = {
        "role": "user",
        "content": (
            f"ЗАДАНИЕ ОТ УЧИТЕЛЯ:\n{prompt}\n\n"
            f"ФАЙЛ ДЛЯ ПРОВЕРКИ: {file_pattern}\n\n"
            f"КОДЫ УЧЕНИКОВ:{pupils_section}"
        ),
    }

    return [sys_msg, user_msg]


def _parse_reviews(content: str, usernames: list[str]) -> list[PupilReview]:
    data = gigachat_client.try_extract_json(content)

    if isinstance(data, dict) and "results" in data:
        reviews: list[PupilReview] = []
        for item in data["results"]:
            reviews.append(
                PupilReview(
                    username=str(item.get("username", "")),
                    correct=bool(item.get("correct", False)),
                    score=int(item.get("score", 0)),
                    summary=str(item.get("summary", "")),
                    suggestions=str(item.get("suggestions", "")),
                )
            )
        return reviews

    return [
        PupilReview(
            username=username,
            correct=False,
            score=0,
            summary=content[:500] if content else "Нет ответа от ИИ.",
            suggestions="Не удалось распарсить ответ ИИ.",
        )
        for username in usernames
    ]


async def check_homework(
    prompt: str,
    file_pattern: str,
    usernames: list[str],
    *,
    max_tool_rounds: int = 5,
    temperature: float = 0.3,
    max_tokens: int = 4000,
) -> list[PupilReview]:
    pupil_codes = _gather_pupil_codes(usernames, file_pattern)
    messages = _build_messages(prompt, file_pattern, pupil_codes)

    content = ""
    for _ in range(max_tool_rounds):
        raw = await gigachat_client.chat_completions(
            messages,
            max_tokens=max_tokens,
            temperature=temperature,
            functions=TOOL_DEFINITIONS,
            function_call="auto",
        )

        choice = raw.get("choices", [{}])[0]
        message = choice.get("message", {})

        fn_call = message.get("function_call")
        if fn_call:
            fn_name = fn_call.get("name", "")
            try:
                fn_args = json.loads(fn_call.get("arguments", "{}"))
            except json.JSONDecodeError:
                fn_args = {}

            messages.append(message)
            result = _execute_tool(fn_name, fn_args, usernames)
            messages.append({"role": "function", "name": fn_name, "content": result})
            continue

        content = message.get("content", "")
        break

    return _parse_reviews(content, usernames)
