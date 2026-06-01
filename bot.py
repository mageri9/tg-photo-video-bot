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


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


stats = {"photos": 0, "videos": 0}


@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer(
        "🎨 *Генератор фото и видео*\n\n"
        "📸 `/photo кот в космосе` — сгенерировать фото (0.30₽)\n"
        "🎬 `/video закат на море` — сгенерировать видео с эффектом наезда (0.30₽)\n"
        "ℹ️ `/stats` — статистика использования\n\n",
        parse_mode=ParseMode.MARKDOWN
    )


@dp.message(Command("photo"))
async def photo_cmd(message: types.Message):
    prompt = message.text.removeprefix("/photo").removeprefix("/video").strip()

    if not prompt:
        await message.answer(
            "❌ Напиши промпт после команды.\nПример: `/photo красивый закат на море`",
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    status_msg = await message.answer("🎨 Генерирую фото... 2-5 секунд")

    try:
        image_url, cost = await asyncio.to_thread(generate_photo, prompt)
        stats["photos"] += 1

        await bot.send_photo(
            message.chat.id,
            image_url,
            caption=f"✅ Готово!\n💰 Стоимость: {cost:.2f}₽\n🎨 {prompt[:100]}",
        )

        await status_msg.delete()

    except Exception as e:
        logger.error(f"Photo generation error: {e}")
        await status_msg.edit_text(f"❌ Ошибка: {str(e)[:200]}")


@dp.message(Command("video"))
async def video_cmd(message: types.Message):
    prompt = message.text.replace("/video", "").strip()

    if not prompt:
        await message.answer(
            "❌ Напиши промпт после команды.\nПример: `/video закат на море`",
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    status_msg = await message.answer("🎬 Генерирую видео... 5-10 секунд")

    video_path = None
    try:
        video_path, cost = await asyncio.to_thread(
            generate_video_from_prompt, prompt, "zoom_in", 5
        )
        stats["videos"] += 1

        video_file = FSInputFile(video_path)
        await bot.send_video(
            message.chat.id,
            video_file,
            caption=f"✅ Видео готово!\n💰 Стоимость: {cost:.2f}₽\n🎬 Эффект: наезд камеры\n🎨 {prompt[:100]}",
        )

        os.remove(video_path)

        await status_msg.delete()

    except Exception as e:
        logger.exception("Photo generation error")

        await status_msg.edit_text(f"❌ Ошибка: {str(e)[:200]}")

    finally:
        if video_path and os.path.exists(video_path):
            os.remove(video_path)


@dp.message(Command("stats"))
async def stats_cmd(message: types.Message):
    total_photos = stats["photos"]
    total_videos = stats["videos"]
    total_cost = (total_photos + total_videos) * 0.30

    await message.answer(
        f"📊 *Статистика использования*\n\n"
        f"📸 Фото: {total_photos}\n"
        f"🎬 Видео: {total_videos}\n"
        f"💰 Всего потрачено: {total_cost:.2f}₽\n\n"
        f"🟢 Бот работает стабильно",
        parse_mode=ParseMode.MARKDOWN,
    )


async def main():
    logger.info("🚀 Бот запущен!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())