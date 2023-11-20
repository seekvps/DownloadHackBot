import os
import time
from ethon.pyfunc import video_metadata
from pyrogram import Client, filters
from pyrogram.enums import MessageMediaType
from pyrogram.errors import (
    ChannelBanned, ChannelInvalid, ChannelPrivate, ChatIdInvalid, ChatInvalid
)
from pyrogram.types import Message
from rich.pretty import pprint
from app.helpers import screenshot, cancelled
from app.progress import progress_for_pyrogram

DownloadList = {}


async def run(bot: Client, user: Client, recv_msg: Message, use_bot=False):
    user_id = recv_msg.chat.id
    link_url = await bot.ask(user_id, "请输入TG分享链接（需要包含多媒体）", filters=filters.text)
    if await cancelled(link_url):
        return
    link_url = link_url.text
    pprint(link_url)

    file_name = str(user_id)

    msg_id = int(link_url.split("/")[-1]) + int(0)

    if 't.me' not in link_url:
        await bot.send_message(user_id, "请提供正确的分享地址，其中要包含字符串 't.me/' ")

    chat = link_url.split("/")[-2]
    if "t.me/c/" in link_url:
        chat = int('-100' + str(chat))

    send_message = await bot.send_message(user_id, "开始下载...")
    edit = await bot.edit_message_text(send_message.chat.id, send_message.id, "正在努力下载...")

    now_client = user
    if use_bot:
        now_client = bot

    raw_msg = None

    try:
        raw_msg = await now_client.get_media_group(chat, msg_id)
    except Exception as e:
        if "The message doesn't belong to a media group" in str(e):
            raw_msg = await now_client.get_messages(chat, msg_id)

    file_list = []

    if isinstance(raw_msg, list):
        for single_msg in raw_msg:
            file_list.append(single_msg)
    else:
        file_list.append(raw_msg)

    media_arr = [MessageMediaType.VIDEO, MessageMediaType.PHOTO, MessageMediaType.VIDEO_NOTE]

    try:
        for msg in file_list:
            if msg.media in media_arr:
                caption = None
                if msg.caption is not None:
                    caption = msg.caption

                if msg.media == MessageMediaType.PHOTO:
                    await edit.edit('正在准备下载')
                    file = await now_client.download_media(
                        msg,
                        file_name="downloads/" + file_name + "/",
                        progress=progress_for_pyrogram,
                        progress_args=(
                            bot,
                            "**下载中:**\n",
                            edit,
                            time.time()
                        )
                    )

                    await edit.edit('正在准备转发')
                    await edit.edit("正在转发中")

                    await bot.send_photo(
                        chat_id=send_message.chat.id,
                        photo=file,
                        caption=caption,
                        progress=progress_for_pyrogram,
                        progress_args=(
                            bot,
                            '**正在转发中:**\n',
                            edit,
                            time.time()
                        )
                    )

                    try:
                        os.remove(file)
                        if os.path.isfile(file):
                            os.remove(file)
                    except Exception:
                        pass

                if msg.media == MessageMediaType.VIDEO:

                    await edit.edit('正在准备下载')
                    file = await now_client.download_media(
                        msg,
                        file_name="downloads/" + file_name + "/",
                        progress=progress_for_pyrogram,
                        progress_args=(
                            bot,
                            "**下载中:**\n",
                            edit,
                            time.time()
                        )
                    )
                    data = video_metadata(file)
                    height, width, duration = data["height"], data["width"], data["duration"]
                    try:
                        thumb_path = await screenshot(file, duration, user_id)
                    except Exception:
                        thumb_path = None
                    await bot.send_video(
                        chat_id=send_message.chat.id,
                        video=file,
                        caption=caption,
                        supports_streaming=True,
                        height=height, width=width, duration=duration,
                        thumb=thumb_path,
                        progress=progress_for_pyrogram,
                        progress_args=(
                            bot,
                            '**正在转发中:**\n',
                            edit,
                            time.time()
                        )
                    )

                    try:
                        os.remove(file)
                        if os.path.isfile(file):
                            os.remove(file)

                        os.remove(thumb_path)
                        if os.path.isfile(thumb_path):
                            os.remove(thumb_path)

                    except Exception:
                        pass
        await edit.delete()
    except ChannelBanned:
        await edit.edit("您貌似被频道屏蔽了")
        return

    except ChannelInvalid:
        await edit.edit("频道格错误")
        return

    except ChannelPrivate:
        await edit.edit("私有频道暂不支持下载")
        return

    except [ChatIdInvalid, ChatInvalid]:
        await edit.edit("您提供的链接地址错误")
        return

    except Exception as e:
        pprint(e)
        await edit.edit("发生了一些意想不到的事情。")
