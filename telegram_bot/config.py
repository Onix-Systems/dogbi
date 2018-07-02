import telepot
from const import bot_token, bot_url

bot = telepot.Bot(bot_token)

bot.setWebhook(bot_url + bot_token)
print("Webhook set!")