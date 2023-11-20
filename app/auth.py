from asyncio.exceptions import TimeoutError

from app.helpers import cancelled
from run import iRedis
from pyrogram import Client, filters
from pyrogram.errors import (
    ApiIdInvalid,
    PhoneNumberInvalid,
    PhoneCodeInvalid,
    PhoneCodeExpired,
    SessionPasswordNeeded,
    PasswordHashInvalid,
)
from pyrogram.types import InlineKeyboardMarkup
from pyrogram.types import Message
from rich.pretty import pprint
from telethon.errors import (
    ApiIdInvalidError,
    PhoneNumberInvalidError,
    PhoneCodeInvalidError,
    PhoneCodeExpiredError,
    SessionPasswordNeededError,
    PasswordHashInvalidError
)
from app.data import Data


async def user_auth(bot: Client, msg: Message, force=False):
    user_id = msg.chat.id
    user_cache_key = "bs" + str(user_id)

    user_session_str = iRedis.get(user_cache_key)
    if force is True:
        user_session_str = None

    auth_user_client = None
    if user_session_str is not None:
        pprint(user_session_str)
        try:
            auth_user_client = Client(
                name=f"user_{user_id}",
                session_string=user_session_str,
                in_memory=False,
                workers=20)
            return auth_user_client
        except Exception as e:
            auth_user_client = None
            pprint(e)

    if auth_user_client is not None:
        return auth_user_client

    send_message = await bot.send_message(user_id, f"若要继续使用需要您进行登录操作。")
    await bot.delete_messages(user_id, send_message.id)
    api_id_msg = await bot.ask(user_id, '请输入您的 `API_ID`', filters=filters.text)
    if await cancelled(api_id_msg):
        return
    try:
        api_id = int(api_id_msg.text)
    except ValueError:
        await api_id_msg.reply(
            'API_ID无效 (必须为数字). 请重新登录。',
            quote=True,
            reply_markup=InlineKeyboardMarkup(Data.generate_button)
        )
        return

    api_hash_msg = await bot.ask(user_id, '请输入您的 `API_HASH`', filters=filters.text)
    if await cancelled(api_hash_msg):
        return
    api_hash = api_hash_msg.text

    t = "请输入您的 `手机号码` 需要加上国家区号. \n 例如 : `+19876543210`'"
    phone_number_msg = await bot.ask(user_id, t, filters=filters.text)
    if await cancelled(phone_number_msg):
        return
    phone_number = phone_number_msg.text
    await msg.reply("正在发送OTP验证，请查看TG官方消息")
    auth_user_client = Client(name=f"user_{user_id}", api_id=api_id, api_hash=api_hash, in_memory=True)
    await auth_user_client.connect()
    try:
        code = await auth_user_client.send_code(phone_number)

    except (ApiIdInvalid, ApiIdInvalidError):
        await msg.reply('`API_ID` 或 `API_HASH` 存在无效值，请重新登录。',
                        reply_markup=InlineKeyboardMarkup(Data.generate_button))
        return
    except (PhoneNumberInvalid, PhoneNumberInvalidError):
        await msg.reply('`手机号码` 无效，请重新登录。',
                        reply_markup=InlineKeyboardMarkup(Data.generate_button))
        return

    try:
        phone_code_msg = await bot.ask(user_id,
                                       "Telegram官方账号将会发送OTP验证码，"
                                       "如果您收到登录验证码, 请按照以下格式发送. "
                                       "\n 例如登录验证码为 `12345`, **请一定按照如下格式发送** `1 2 3 4 5`.",
                                       filters=filters.text, timeout=600)
        if await cancelled(phone_code_msg):
            return

    except TimeoutError:
        await msg.reply('超过最大验证次数，请10分钟后继续使用。',
                        reply_markup=InlineKeyboardMarkup(Data.generate_button))
        return

    phone_code = phone_code_msg.text.replace(" ", "")
    try:
        await auth_user_client.sign_in(phone_number, code.phone_code_hash, phone_code)

    except (PhoneCodeInvalid, PhoneCodeInvalidError):
        await msg.reply('验证码错误，请重试。',
                        reply_markup=InlineKeyboardMarkup(Data.generate_button))
        return
    except (PhoneCodeExpired, PhoneCodeExpiredError):
        await msg.reply('验证码过期，请重试。',
                        reply_markup=InlineKeyboardMarkup(Data.generate_button))
        return
    except (SessionPasswordNeeded, SessionPasswordNeededError):
        try:
            two_step_msg = await bot.ask(user_id,
                                         '您的账号开启了2步验证，请您的输入密码。',
                                         filters=filters.text, timeout=300)
        except TimeoutError:
            await msg.reply('5分钟超时，请重试。',
                            reply_markup=InlineKeyboardMarkup(Data.generate_button))
            return
        try:
            password = two_step_msg.text
            await auth_user_client.check_password(password=password)

            if await cancelled(api_id_msg):
                return
        except (PasswordHashInvalid, PasswordHashInvalidError):
            await two_step_msg.reply('密码错误，请重试', quote=True,
                                     reply_markup=InlineKeyboardMarkup(Data.generate_button))
            return

    session_str = await auth_user_client.export_session_string()
    iRedis.set(user_cache_key, session_str)
    return auth_user_client


