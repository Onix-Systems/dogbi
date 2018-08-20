import sys
import asyncio
import random
import telepot
import os
from telepot.aio.loop import MessageLoop
from telepot.aio.delegate import per_chat_id, create_open, pave_event_space
from const import TOKEN
from answers import ANSWERS
from AI.image import merge, crop

BASE = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'downloaded_images')


class ChatUser(telepot.aio.helper.ChatHandler):

    # Needed for an initial message differantiation
    # Dogbi treats every message the same
    async def open(self, initial_msg, seed):
        pass

    async def on_chat_message(self, msg):
        content_type, chat_type, chat_id = telepot.glance(msg)
        print(content_type, chat_type, chat_id)
        language = 'EN'
        # Handle Photos
        if content_type == 'photo':
            # Get the photo with the most quality
            file_id = msg['photo'][-1]['file_id']
            path = os.path.join(BASE, file_id + ".jpg")
            await bot.download_file(
                file_id,
                path
            )
            # If the crop failed, it means there are no dogs or humans
            if crop(path) is False:
                response = ANSWERS[language].get("not_found")
                await self.sender.sendMessage(response, parse_mode="HTML")
                return
            return

        # Handle Commands
        if content_type == 'text':
            # Ignore the slash
            command = msg['text'][1:]
            # Get the wanted command in the language dict
            response = ANSWERS[language].get(command)
            # Return Help if the command is not found
            await self.sender.sendMessage(response or ANSWERS[language].get("help"), parse_mode="HTML")
            return

        # Handle Buttons
        if content_type == 'callback':
            await self.sender.sendMessage("you pressed a button")
            return

    # Sent when a timeout expires
    async def on__idle(self, event):
        pass


bot = telepot.aio.DelegatorBot(TOKEN, [
    pave_event_space()(
        per_chat_id(), create_open, ChatUser, timeout=10),
])

loop = asyncio.get_event_loop()
loop.create_task(MessageLoop(bot).run_forever())
print('Listening ...')

loop.run_forever()
