import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import FSInputFile
from aiogram.enums import ParseMode

from config import BOT_TOKEN
from image_gen import generate_photo
from video_gen import generate_video_from_prompt
from translation_cost import calculate_translation_cost

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

stats = {"photos": 0, "videos": 0, "translation_cost": 0.0}


@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer(
        "🎨 *Генератор фото и видео*\n\n"
        "📸 `/photo кот` — фото (0.30₽ + перевод)\n"
        "🎬 `/video закат` — видео с наездом камеры (0.30₽ + перевод)\n"
        "ℹ️ `/stats` — статистика\n\n"
        "💰 Цена перевода: 0.0235₽ за слово",
        parse_mode=ParseMode.MARKDOWN,
    )


@dp.message(Command("photo"))
async def photo_cmd(message: types.Message):
    prompt = message.text.removeprefix("/photo").strip()

    if not prompt:
        await message.answer(
            "❌ Напиши промпт. Пример: `/photo закат`", parse_mode=ParseMode.MARKDOWN
        )
        return

    translation_cost = calculate_translation_cost(prompt)
    status_msg = await message.answer("🎨 Генерирую фото... 2-5 секунд")

    try:
        image_url, gen_cost = await asyncio.to_thread(generate_photo, prompt)
        total_cost = gen_cost + translation_cost

        stats["photos"] += 1
        stats["translation_cost"] += translation_cost

        await bot.send_photo(
            message.chat.id,
            image_url,
            caption=f"✅ Готово!\n💰 {total_cost:.2f}₽ (генерация {gen_cost:.2f}₽ + перевод {translation_cost:.2f}₽)\n🎨 {prompt[:100]}",
        )
        await status_msg.delete()

    except Exception:
        logger.exception("Photo generation error")
        await status_msg.edit_text("❌ Ошибка при генерации фото")


@dp.message(Command("video"))
async def video_cmd(message: types.Message):
    prompt = message.text.removeprefix("/video").strip()

    if not prompt:
        await message.answer(
            "❌ Напиши промпт. Пример: `/video закат`", parse_mode=ParseMode.MARKDOWN
        )
        return

    translation_cost = calculate_translation_cost(prompt)
    status_msg = await message.answer("🎬 Генерирую видео... 5-10 секунд")
    video_path = None

    try:
        video_path, gen_cost = await asyncio.to_thread(
            generate_video_from_prompt, prompt, "zoom_in", 5
        )
        total_cost = gen_cost + translation_cost

        stats["videos"] += 1
        stats["translation_cost"] += translation_cost

        video_file = FSInputFile(video_path)
        await bot.send_video(
            message.chat.id,
            video_file,
            caption=f"✅ Видео готово!\n💰 {total_cost:.2f}₽ (генерация {gen_cost:.2f}₽ + перевод {translation_cost:.2f}₽)\n🎨 {prompt[:100]}",
        )
        await status_msg.delete()

    except Exception:
        logger.exception("Video generation error")
        await status_msg.edit_text("❌ Ошибка при генерации видео")

    finally:
        if video_path and os.path.exists(video_path):
            os.remove(video_path)


@dp.message(Command("stats"))
async def stats_cmd(message: types.Message):
    total_generations = stats["photos"] + stats["videos"]
    generation_cost = total_generations * 0.30
    total_cost = generation_cost + stats["translation_cost"]

    await message.answer(
        f"📊 *Статистика*\n\n"
        f"📸 Фото: {stats['photos']}\n"
        f"🎬 Видео: {stats['videos']}\n"
        f"💰 За генерацию: {generation_cost:.2f}₽\n"
        f"📝 За перевод: {stats['translation_cost']:.2f}₽\n"
        f"💸 *Всего: {total_cost:.2f}₽*",
        parse_mode=ParseMode.MARKDOWN,
    )


async def main():
    logger.info("🚀 Бот запущен")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())