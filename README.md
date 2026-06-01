[Демо]<img width="1183" height="1001" alt="Image" src="https://github.com/user-attachments/assets/a31a7c48-1965-49d8-8167-af34f8e28474" />](https://github.com/mageri9/tg-photo-video-bot/issues/1#issue-4561237030)

## 📊 Анализ цен (за 1 фото)

| Провайдер | Цена | Модель | Вердикт |
| :--- | :--- | :--- | :--- |
| aitunnel | 0.82 ₽ | GPT Image 1 Mini | 🟡 Дорого |
| proxyapi | 1.52 ₽ | GPT Image 1 Mini | 🔴 Переплата |
| vsellm | 2 ₽ | GPT Image 1 Mini | 🔴 Переплата x2.4 |
| **gen-api.ru** | **~0.30 ₽** | **SDXL Lightning** | ✅ **Выбор** |
| gen-api.ru | 0.25 ₽ | Xailab NSFW | ⚠️ Специфика |
| Kandinsky | бесплатно | Kandinsky 3.1 | ⚠️ Есть лимиты |

**Итог:** наша цена **0.20 - 0.30 ₽ + перевод**

Самый простой способ удешевить видео - рендерить статику.
Либо же селф-хостинг.

```markdown
# 🎨 Фото + Видео бот

## Команды

```
/photo кот          → фото
/video закат        → видео (наезд камеры, 5 сек)
/stats              → статистика
```

## Запуск

```bash
pip install -r requirements.txt
python bot.py
```
Не забудь вставить токены в .env

## Технологии

- SDXL Lightning (gen-api.ru)
- MoviePy
- Aiogram 3


--

**Итог:** наша цена **0.20 - 0.30 ₽ + перевод**

Самый простой способ удешевить видео - рендерить статику.
Либо же селф-хостинг.
