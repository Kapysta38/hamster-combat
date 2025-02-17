from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from aiogram.utils import executor

# Укажите токен вашего бота
# Удалил действующий токен и отключил его действие через бота отца
TOKEN = ''  # Замените на токен вашего бота

# Инициализация бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)


# Обработчик команды /start
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    # Создаем кнопку для открытия Web App
    web_app_url = "https://45.82.153.232"  # Замените на URL вашего приложения
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(InlineKeyboardButton(text="Open Web App", web_app=WebAppInfo(url=web_app_url)))

    await message.reply("Нажми чтобы начать тапать хомяка:", reply_markup=keyboard)


# Запуск бота
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
