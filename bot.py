import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage
import os

TOKEN = os.getenv("8226904305:AAGEMPi6l0Cn_dd2hwedsfw0yUQEnCbGDok")
ADMIN_ID = 7638020501

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

class Form(StatesGroup):
    action = State()
    account_id = State()
    amount = State()

@dp.message(CommandStart())
async def start(message: types.Message, state: FSMContext):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💰 Пополнить", callback_data="deposit")],
        [InlineKeyboardButton(text="💸 Вывести", callback_data="withdraw")]
    ])
    await message.answer("Выберите действие:", reply_markup=kb)

@dp.callback_query(lambda c: c.data in ["deposit", "withdraw"])
async def choose_action(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(action=callback.data)
    await state.set_state(Form.account_id)
    await callback.message.answer("Введите ID аккаунта:")
    await callback.answer()

@dp.message(Form.account_id)
async def get_account(message: types.Message, state: FSMContext):
    await state.update_data(account_id=message.text)
    await state.set_state(Form.amount)
    await message.answer("Введите сумму:")

@dp.message(Form.amount)
async def get_amount(message: types.Message, state: FSMContext):
    data = await state.get_data()
    action = "Пополнение" if data["action"] == "deposit" else "Вывод"

    text = (
        f"📥 Новая заявка\n\n"
        f"Тип: {action}\n"
        f"Пользователь: @{message.from_user.username} ({message.from_user.id})\n"
        f"ID аккаунта: {data['account_id']}\n"
        f"Сумма: {message.text}"
    )

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"ok:{message.from_user.id}"),
            InlineKeyboardButton(text="❌ Отклонить", callback_data=f"no:{message.from_user.id}")
        ]
    ])

    await bot.send_message(ADMIN_ID, text, reply_markup=kb)
    await message.answer("✅ Заявка отправлена, ожидайте решения.")
    await state.clear()

@dp.callback_query(lambda c: c.data.startswith(("ok:", "no:")))
async def admin_decision(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("Нет доступа", show_alert=True)
        return

    action, user_id = callback.data.split(":")
    user_id = int(user_id)

    if action == "ok":
        await bot.send_message(user_id, "✅ Ваша заявка подтверждена")
        await callback.message.edit_text(callback.message.text + "\n\n✅ Подтверждено")
    else:
        await bot.send_message(user_id, "❌ Ваша заявка отклонена")
        await callback.message.edit_text(callback.message.text + "\n\n❌ Отклонено")

    await callback.answer()

async def main():
    await dp.start_polling(bot)

if name == "__main__":
    asyncio.run(main())
