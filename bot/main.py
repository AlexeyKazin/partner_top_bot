import logging
import os
import asyncio
from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.contrib.fsm_storage.memory import MemoryStorage

API_TOKEN = os.getenv("API_TOKEN")
ADMIN_ID = 271359835

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

users = {}
payments = {}
referrals = {}
balances = {}

@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    ref = message.get_args()

    if user_id not in users:
        users[user_id] = {'paid': False}
        if ref and ref.isdigit() and int(ref) != user_id:
            referrals[user_id] = int(ref)

    if users[user_id]['paid']:
        await message.answer("Вы уже оплатили доступ. Вот ссылка на клуб и курс:\nhttps://t.me/your_club\nhttps://t.me/your_course")
    else:
        kb = InlineKeyboardMarkup().add(
            InlineKeyboardButton("Оплатить 300₽", url="https://yoomoney.ru/pay")
        )
        await message.answer("Для доступа к клубу требуется оплата 300₽. Нажмите кнопку ниже для оплаты.", reply_markup=kb)
        await asyncio.sleep(3600)
        if not users[user_id]['paid']:
            await message.answer("Не забудьте оплатить, чтобы начать зарабатывать уже сейчас!")
        await asyncio.sleep(86400 - 3600)
        if not users[user_id]['paid']:
            await message.answer("Начни зарабатывать уже сейчас!")

@dp.message_handler(commands=['pay'])
async def cmd_pay(message: types.Message):
    user_id = message.from_user.id
    users[user_id]['paid'] = True
    payments[user_id] = 300

    ref_id = referrals.get(user_id)
    if ref_id:
        balances[ref_id] = balances.get(ref_id, 0) + 100

    await message.answer("Оплата прошла успешно! Вот ссылка на клуб и курс:\nhttps://t.me/your_club\nhttps://t.me/your_course")

@dp.message_handler(commands=['admin'])
async def cmd_admin(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    total_users = len(users)
    paid_users = sum(1 for u in users.values() if u['paid'])
    total_payments = sum(payments.values())
    total_cashback = sum(balances.values())
    profit = total_payments - total_cashback
    net_profit = profit * 0.93
    await message.answer(
        f"Всего пользователей: {total_users}\n"
        f"Оплатили: {paid_users}\n"
        f"Сумма оплат: {total_payments}₽\n"
        f"Сумма кэшбека: {total_cashback}₽\n"
        f"Прибыль: {net_profit:.2f}₽"
    )

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    executor.start_polling(dp, skip_updates=True)
