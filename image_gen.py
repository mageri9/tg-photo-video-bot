import time
import requests
from config import GEN_API_KEY, PHOTO_COST_RUB

NETWORK_ID = "sdxl-lightning"

BASE_URL = "https://api.gen-api.ru/api/v1"

def generate_photo(prompt: str, width: int = 1024, height: int = 1024):
    """
    Генерация фото через SDXL Lightning (gen-api.ru)
    Возвращает: (image_url, cost_rub)
    """
    headers = {
        "Authorization": f"Bearer {GEN_API_KEY}",
        "Content-Type": "application/json",
    }

    # ЗАПРОС
    payload = {
        "model": "standard",
        "prompt": prompt,
        "width": width,
        "height": height,
    }

    response = requests.post(
        f"{BASE_URL}/networks/{NETWORK_ID}",
        json=payload,
        headers=headers,
        timeout=30,
    )
    response.raise_for_status()

    data = response.json()
    request_id = data.get("request_id")

    if not request_id:
        raise Exception("Не получен request_id от API")

    # РЕЗУЛЬТАТ
    max_attempts = 30
    attempt = 0

    while attempt < max_attempts:
        try:
            result_response = requests.get(
                f"{BASE_URL}/request/get/{request_id}",
                headers=headers,
                timeout=30,
            )
            result_response.raise_for_status()
            result = result_response.json()

            status = result.get("status")

            if status == "completed":
                images = result.get("result")

                if not images:
                    raise Exception("Пустой результат генерации")

                image_url = images[0]

                return image_url, PHOTO_COST_RUB

            elif status == "failed":
                error = result.get("error", "Неизвестная ошибка")
                raise Exception(f"Генерация не удалась: {error}")

            time.sleep(1)
            attempt += 1

        except requests.exceptions.RequestException as e:
            raise e

    raise Exception("Таймаут ожидания генерации")