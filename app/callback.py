from app.auth import user_auth, download
from app.data import Data
from pyrogram import Client
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup

auth_user_client = {}


# Callbacks
@Client.on_callback_query()
async def _callbacks(bot: Client, callback_query: CallbackQuery):
    user = await bot.get_me()
    user_id = callback_query.from_user.id
    mention = user.mention

    query = callback_query.data.lower()

    if query == "download":
        chat_id = callback_query.from_user.id
        message_id = callback_query.message.id
        if user_id in auth_user_client:
            now_user_client = auth_user_client[user_id]
            now_user_info = await now_user_client.get_me()
            await bot.send_message(chat_id, "当前已登录用户:" + now_user_info.mention)

        else:
            await callback_query.answer(
                "请注意，想要下载受保护的内容需要进行登录操作（Bot是存在极限的）",
                show_alert=True)
            now_user_client = await user_auth(bot, callback_query.message)
            try:
                now_user_info = await now_user_client.get_me()
            except Exception as e:
                now_user_client = await user_auth(bot, callback_query.message, True)
                now_user_info = await now_user_client.get_me()

            auth_user_client[user_id] = now_user_client
            await bot.send_message(chat_id, "当前登录用户:" + now_user_info.mention)

        await download(bot, now_user_client, callback_query.message)

    if query == 'download_normal':
        chat_id = callback_query.from_user.id
        message_id = callback_query.message.id

        await download(bot, bot, callback_query.message, True)

    if query == 'home':
        chat_id = callback_query.from_user.id
        message_id = callback_query.message.id
        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=Data.START.format(callback_query.from_user.mention, mention),
            reply_markup=InlineKeyboardMarkup(Data.buttons),
        )

    if query == "about":
        chat_id = callback_query.from_user.id
        message_id = callback_query.message.id
        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=Data.ABOUT,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(Data.home_buttons),
        )

    if query == "help":
        chat_id = callback_query.from_user.id
        message_id = callback_query.message.id
        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=Data.HELP,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(Data.home_buttons),
        )
