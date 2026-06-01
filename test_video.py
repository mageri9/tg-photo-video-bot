import os
import requests
from moviepy_presets import render_ken_burns_mp4

# 1. Скачай любую тестовую картинку (или используй свою)
test_image_url = "https://picsum.photos/1024/1024"  # случайное фото с сервиса

response = requests.get(test_image_url)
with open("test_image.jpg", "wb") as f:
    f.write(response.content)

print("✅ Картинка скачана")

# 2. Проверяем каждый пресет
presets = ["zoom_in", "zoom_out", "pan_left", "pan_right", "pan_up", "pan_down", "diag"]

for preset in presets:
    out_path = f"test_{preset}.mp4"
    print(f"🎬 Генерирую {preset}...")

    render_ken_burns_mp4(
        image_path="test_image.jpg",
        out_mp4_path=out_path,
        preset=preset,
        duration=4,  # 4 секунды для теста
        fps=24,
        out_size=(854, 480),  # уменьшенный размер для быстрого теста
    )

    print(f"   ✅ {out_path} создан, размер: {os.path.getsize(out_path)} байт")

print("\n🎉 Все тесты прошли! Файлы:")
for preset in presets:
    print(f"   - test_{preset}.mp4")

# Чистим временную картинку
os.remove("test_image.jpg")