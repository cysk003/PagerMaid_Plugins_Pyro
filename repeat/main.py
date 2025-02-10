import json
import os

from pagermaid.listener import listener
from pagermaid.enums import Message
from pagermaid.utils.bot_utils import log
from pyrogram.enums import ChatType
from pyromod.listen import Client

# 持久化存储回复对象
repeat_status_file = 'data/repeat_status.json'

# 加载状态
def load_repeat_status():
    if os.path.exists(repeat_status_file):
        with open(repeat_status_file, 'r') as f:
            return json.load(f)
    return {}

# 保存状态
def save_repeat_status(data):
    with open(repeat_status_file, 'w') as f:
        json.dump(data, f)

# 初始化
repeat_status = load_repeat_status()

@listener(command="repeat", description="自动复读（无引用）一个人的消息", parameters="<[reply]|status>")
async def repeat(context: Message):
    if context.chat.type not in [ChatType.GROUP, ChatType.SUPERGROUP]:
        await context.edit('请在群组中运行。')
        return
    reply = context.reply_to_message
    if not reply or not reply.from_user:
        await context.edit('请回复一个用户。')
        return
    uid = reply.from_user.id
    chat_id = context.chat.id
    if context.parameter:
        if repeat_status.get(f'{chat_id}_{uid}'):
            await context.edit('此用户存在于自动复读列表。')
        else:
            await context.edit('此用户不存在于自动复读列表。')
        return
    if repeat_status.get(f'{chat_id}_{uid}'):
        del repeat_status[f'{chat_id}_{uid}']
        await context.edit('从自动复读列表移除成功。')
    else:
        repeat_status[f'{chat_id}_{uid}'] = 'true'
        await context.edit('添加到自动复读列表成功。')
    save_repeat_status(repeat_status)

@listener(incoming=True, ignore_edited=True)
async def repeat_msg(context: Message, bot: Client):
    """ Event handler. """
    chat_id = context.chat.id
    if not context.from_user:
        return
    sender_id = context.from_user.id
    if repeat_status.get(f'{chat_id}_{sender_id}'):
        try:
            msg = context.text
            return await bot.send_message(context.chat.id, msg)
        except Exception as e:
            await log(f'Repeat Error:\n{e}')
