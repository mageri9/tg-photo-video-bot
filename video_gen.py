import os
import uuid
import requests
from moviepy_presets import render_ken_burns_mp4
from image_gen import generate_photo
from config import VIDEO_COST_RUB

def download_image(url: str) -> str:
    """Скачивает изображение по URL во временный файл"""
    filename = f"temp_{uuid.uuid4().hex}.jpg"
    response = requests.get(url, timeout=60)
    response.raise_for_status()

    with open(filename, "wb") as f:
        f.write(response.content)

    return filename

def generate_video_from_prompt(
    prompt: str,
    preset: str = "zoom_out",
    duration: float = 6.0,
    fps: int = 30,
    out_size: tuple = (1280, 720),
) -> tuple:
    """
    Полный пайплайн: генерация фото → превращение в видео с Ken Burns эффектом

    preset: zoom_in, zoom_out, pan_left, pan_right, pan_up, pan_down, diag

    Возвращает: (video_file_path, cost_rub)
    """

    image_url, photo_cost = generate_photo(prompt)

    image_path = download_image(image_url)

    video_filename = f"video_{uuid.uuid4().hex}.mp4"
    video_path = render_ken_burns_mp4(
        image_path=image_path,
        out_mp4_path=video_filename,
        preset=preset,
        duration=duration,
        fps=fps,
        out_size=out_size
    )

    os.remove(image_path)

    return video_path, VIDEO_COST_RUB