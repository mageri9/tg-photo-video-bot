import asyncio
import os
import uuid
import aiohttp
from moviepy_presets import render_ken_burns_mp4
from image_gen import generate_photo
from config import VIDEO_COST_RUB


async def download_image(url: str) -> str:
    """Асинхронно скачивает изображение по URL во временный файл"""
    filename = f"temp_{uuid.uuid4().hex}.jpg"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            response.raise_for_status()
            content = await response.read()
            with open(filename, "wb") as f:
                f.write(content)
    return filename


async def generate_video_from_prompt(
    prompt: str,
    preset: str = "zoom_in",
    duration: float = 6.0,
    fps: int = 30,
    out_size: tuple = (1280, 720)
) -> tuple:
    """
    Полный пайплайн: асинхронная генерация фото → превращение в видео
    Возвращает: (video_file_path, cost_rub)
    """
    image_url, photo_cost = await generate_photo(prompt)

    image_path = await download_image(image_url)

    video_filename = f"video_{uuid.uuid4().hex}.mp4"
    video_path = await asyncio.to_thread(
        render_ken_burns_mp4,
        image_path,
        video_filename,
        preset,
        duration,
        fps,
        out_size
    )

    os.remove(image_path)

    return video_path, VIDEO_COST_RUB