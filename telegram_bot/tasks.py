from __future__ import absolute_import, unicode_literals
from dog_bot.celery import app
from AI.classify_singleton import Analyzer
from AI.image import merge, crop
from telegram_bot import models
from telegram_bot import const
import telepot
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton

BOT = telepot.Bot(const.bot_token)


def send_photo(user, image_name):
    path = const.media_url + image_name.replace(' ', '_') + '.jpg'
    try:
        BOT.sendPhoto(user.user_id, path)
    except Exception as e:
        print("Error sending a photo of a breed: " + path + str(e))


def send_results(user, response):
    if user.language == 'RU':
        r = "Я думаю это " + response[0][0] + " и я на " + str(response[1][0] * 100)[
                                                           :4] + "% уверен. Я отослал Вам фотографию, можете проверить сами. Я думаю это также может быть: " + \
            response[0][1] + " или " + response[0][2] + " (нажмите, чтобы получить фотографию)."
        wrong_button = "Неправильно" + u"\u2620"
    else:
        r = "I think the breed of this dog is " + response[0][0] + " and I'm " + str(response[1][0] * 100)[
                                                                                 :4] + "% confident. I sent you a photo, so you can see for yourself. I also found it similar to the following breeds: " + \
            response[0][1] + ", " + response[0][2] + " (tap to get a photo)."
        wrong_button = "Wrong" + u"\u2620"

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=response[0][1], callback_data='dog ' + response[0][1]),
                InlineKeyboardButton(text=response[0][2], callback_data='dog ' + response[0][2]),
                InlineKeyboardButton(text=wrong_button, callback_data='wrong'),
            ]
        ]
    )
    BOT.sendMessage(user.user_id, text=r, reply_markup=keyboard)


def get_user(user_id):
    try:
        user = models.UserLang.objects.get(user_id=user_id)
    except models.UserLang.DoesNotExist:
        user = models.UserLang.objects.create(
            user_id=user_id
        )
    return user


@app.task
def analyze(path, user_id):
    # Getting the user
    user = get_user(user_id)
    # Cropping the image
    if crop(path) is False:
        BOT.sendMessage(user.user_id, "Please, send another picture!")
        return 1
    # Initializing the analyzer and getting the result
    analyzer = Analyzer()
    response = analyzer.get_score(path)
    user.files.add(models.File.objects.create(path=path))

    try:
        merged_image = merge(path, response[0][0].replace(' ', '_'), user.user_id, response[1][0])
        user.files.add(models.File.objects.create(path=merged_image))
        send_photo(user, merged_image)
    except Exception as e:
        print("Error sending merged: " + str(e))
    send_results(user, response)

    user.save()
    return 0
