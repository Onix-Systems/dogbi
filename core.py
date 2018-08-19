import sys
import asyncio
import random
import telepot
import os
from telepot.aio.loop import MessageLoop
from telepot.aio.delegate import per_chat_id, create_open, pave_event_space
from telegram_bot.const import bot_token
from answers import ANSWERS

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'downloaded_images')


class ChatUser(telepot.aio.helper.ChatHandler):

    # Needed for an initial message differantiation
    # Dogbi treats every message the same
    async def open(self, initial_msg, seed):
        pass

    async def on_chat_message(self, msg):
        content_type, chat_type, chat_id = telepot.glance(msg)
        print(content_type, chat_type, chat_id)
        # Handle Photos
        if content_type == 'photo':
            print(msg['photo'][-1]['file_id'])
            file_id = msg['photo'][-1]['file_id']
            path = os.path.join(BASE, file_id + ".jpg")
            await bot.download_file(
                file_id,
                path
            )
            return
        # Handle Commands
        if content_type == 'text':
            language = 'EN'
            command = msg['text'][1:]
            response = ANSWERS[language].get(command)
            await self.sender.sendMessage(response or ANSWERS[language].get("help"), parse_mode="HTML")
            return
        # Handle Buttons
        if content_type == 'callback':
            await self.sender.sendMessage("you pressed a button")
            return

    # Sent when a timeout expires
    async def on__idle(self, event):
        pass


TOKEN = bot_token

bot = telepot.aio.DelegatorBot(TOKEN, [
    pave_event_space()(
        per_chat_id(), create_open, ChatUser, timeout=10),
])

loop = asyncio.get_event_loop()
loop.create_task(MessageLoop(bot).run_forever())
print('Listening ...')

loop.run_forever()
