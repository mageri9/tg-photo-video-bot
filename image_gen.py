import time
import requests
import logging
from config import GEN_API_KEY, PHOTO_COST_RUB

logger = logging.getLogger(__name__)

NETWORK_ID = "sdxl-lightning"

BASE_URL = "https://api.gen-api.ru/api/v1"


def generate_photo(prompt: str, width: int = 1024, height: int = 1024):
    """
    Генерация фото через SDXL Lightning (gen-api.ru)
    Возвращает: (image_url, cost_rub)
    """
    headers = {
        "Authorization": f"Bearer {GEN_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "standard",
        "prompt": prompt,
        "width": width,
        "height": height
    }

    logger.info(f"Отправка запроса к {BASE_URL}/networks/{NETWORK_ID}")
    response = requests.post(
        f"{BASE_URL}/networks/{NETWORK_ID}",
        json=payload,
        headers=headers,
        timeout=30
    )
    response.raise_for_status()

    data = response.json()
    logger.info(f"Ответ на запрос: {data}")

    request_id = data.get("request_id")

    if not request_id:
        raise Exception(f"Не получен request_id. Ответ API: {data}")

    max_attempts = 60  # 60 секунд максимум
    attempt = 0

    while attempt < max_attempts:
        result_response = requests.get(
            f"{BASE_URL}/request/get/{request_id}",
            headers=headers,
            timeout=10
        )
        result_response.raise_for_status()
        result = result_response.json()

        logger.info(f"Попытка {attempt + 1}: статус {result.get('status')}")

        status = result.get("status")

        if status in ["completed", "success"]:
            result_array = result.get("result", [])
            if not result_array:
                raise Exception("Результат генерации не содержит URL")

            image_url = result_array[0]
            logger.info(f"Генерация завершена, URL: {image_url}")


            cost_rub = PHOTO_COST_RUB

            return image_url, cost_rub

        elif status == "failed":
            error = result.get("error", "Неизвестная ошибка")
            raise Exception(f"Генерация не удалась: {error}")

        time.sleep(1)
        attempt += 1

    raise Exception(f"Таймаут ожидания генерации. request_id={request_id}")