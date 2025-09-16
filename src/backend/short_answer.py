import aiohttp
import asyncio
import json

folder_id = "b1gsektsm3sqcamqu30q"
yandexgpt_api_key = ""
yandex_gpt_api_url = ''


async def yandex_gpt(messages: list):
    async with aiohttp.ClientSession() as session:
        async with session.post(
                yandex_gpt_api_url,
                headers={
                    "Authorization": f"Api-Key {yandexgpt_api_key}",
                    "x-folder-id": folder_id
                },
                json={
                    "modelUri": f"gpt://{folder_id}/yandexgpt/latest",
                    "completionOptions": {
                        "stream": False,
                        "temperature": 0.2
                    },
                    "messages": messages
                }
        ) as response:
            return await response.json()


async def get_short_answer(prompt: str, document: str, question: str) -> str:
    messages = [
        {
            "role": "system",
            "text": f"{prompt}"
        },
        {
            "role": "user",
            "text": f"Документ:\n{document}"
        },
        {
            "role": "user",
            "text": f"Вопрос\n{question}"
        }
    ]

    response = await yandex_gpt(messages)
    return response['result']['alternatives'][0]['message']['text']
