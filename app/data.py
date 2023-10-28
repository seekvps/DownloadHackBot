from pyrogram.types import InlineKeyboardButton


class Data:
    generate_single_button = [InlineKeyboardButton("🔥 开始 🔥", callback_data="download")]

    home_buttons = [
        generate_single_button,
        [InlineKeyboardButton(text="🏠 主页 🏠", callback_data="home")]
    ]

    generate_button = [generate_single_button]

    buttons = [
        generate_single_button,
        [
            InlineKeyboardButton("帮助 ❔", callback_data="help"),
            InlineKeyboardButton("🎪 关于 🎪", callback_data="about")
        ]
    ]

    START = """
Hey {}

Welcome to {}

本Bot不存储利用您的任何个人信息,请放心使用。如果您存在顾虑请按照以下步骤清除： 
1) 删除停用本Bot
2) 设置-设备中清除登录历史

如过您觉得没问题?
您将可以下载群组或者频道内容受保护的视频与图片. 
注：如您使用本Bot，需要到 https://my.telegram.org/auth 注册一个开发者APP

By @DownloadHackBot
    """

    HELP = """
✨ ** 可用指令集 ** ✨

/help - 帮助指令
/start - 开始使用（需用户登录）
/about - 关于
/cancel - 取消操作

"""

    ABOUT = """
**关于** 

无聊之间把之前写的两个小工具完善了一下，目前处于测试阶段，如果有意想不到的Bug，请联系我。

    """
