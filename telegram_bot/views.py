from django.views import generic
from django.http.response import HttpResponse
import json
from pprint import pprint
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from telegram_bot import const
import telepot
import os
from . import models
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from AI.classify_singleton import Analyzer
from shutil import copy
from AI.image import merge, crop
import requests
from AI.find_translation import find_translation

command_list = ['/start', '/help', '/language', '/about']


class BotView(generic.View):
    BOT = telepot.Bot(const.bot_token)
    BASE = os.path.dirname(os.path.abspath(__file__))
    analyzer = Analyzer()

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return generic.View.dispatch(self, request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        try:
            incoming_message = json.loads(self.request.body.decode('utf-8'))
            pprint(incoming_message)
            try:
                tele_id = incoming_message['message']['from']['id']
            except KeyError:
                tele_id = incoming_message['callback_query']['from']['id']
            try:
                user = models.UserLang.objects.get(user_id=tele_id)
            except models.UserLang.DoesNotExist:
                user = models.UserLang.objects.create(
                    user_id=tele_id
                )
            try:
                callback = incoming_message['callback_query']['data']
                text = ''
            except KeyError:
                callback = ''
                try:
                    text = incoming_message['message']['text']
                except KeyError:
                    text = ''
            try:
                if callback is not '':
                    if 'RU' in callback or 'EN' in callback:
                        self.set_language(user, callback)
                    if 'dog' in callback:
                        self.send_photo_of_a_breed(user, callback[4:])
                    if 'wrong' in callback:
                        self.wrong_result(user)
                    pprint("returning")
                    return HttpResponse()
                if 'photo' not in incoming_message['message']:
                    if text == '/start' or text == '/help' or text not in command_list:
                        self.send_help_menu(user)
                        return HttpResponse()
                    if text == '/about':
                        self.send_about_menu(user)
                        return HttpResponse()
                    if text == '/language':
                        self.send_language_selection_menu(user)
                        return HttpResponse()
                else:
                    self.send_processing(user)

                    file_id = incoming_message['message']['photo'][-1]['file_id']
                    path = os.path.join(self.BASE, file_id + ".jpg")
                    self.delete_files(user)
                    self.BOT.download_file(
                        file_id,
                        path
                    )
                    if crop(path) is False:
                        self.BOT.sendMessage(user.user_id, "Please, send another picture!")
                        return HttpResponse()
                    response = self.analyzer.get_score(path)
                    try:
                        if user.language == RU:
                            merged_image = merge(path, response[0][0].replace(' ', '_'), user.user_id, response[1][0], localize=True)
                        else:
                            merged_image = merge(path, response[0][0].replace(' ', '_'), user.user_id, response[1][0])
                        self.send_photo_of_a_breed(user, merged_image)
                    except Exception as e:
                        pprint("Error sending merged: " + str(e))
                    self.send_results(user, response)
                    user.files.add(models.File.objects.create(path=path))
                    user.files.add(models.File.objects.create(path=merged_image))
                    user.save()
                    return HttpResponse()
            except telepot.exception.BotWasBlockedError:
                return HttpResponse()
        except Exception as e:
            pprint(e)
            return HttpResponse()
        return HttpResponse()

    def get(self, request, *args, **kwargs):
        return HttpResponse("hey!")

    def send_language_selection_menu(self, user):
        if user.language == 'RU':
            selection_text = "Выберите язык"
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(text="Английский", callback_data='EN'),
                        InlineKeyboardButton(text="Русский", callback_data='RU'),
                    ]
                ]
            )
        else:
            selection_text = "Select your preferred language"
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(text="English", callback_data='EN'),
                        InlineKeyboardButton(text="Russian", callback_data='RU'),
                    ]
                ]
            )
        self.BOT.sendMessage(user.user_id, text=selection_text, reply_markup=keyboard)

    def send_help_menu(self, user):
        if user.language == 'RU':
            help_text = "Вы можете использовать этого бота отослав ему фотографию собаки. Он обработает изображение и попытается определить породу. Вы можете использовать /language для смены языка."
        else:
            help_text = "You can use this bot by sending a photo of a dog. It will process the image and try to identify the dog\'s breed. You can use /language command for chaning the language"

        self.BOT.sendMessage(
            user.user_id,
            help_text
        )

    def send_results(self, user, response):
        if user.language == 'RU':
            r = "Я думаю это " + find_translation(response[0][0]) + " и я на " + str(response[1][0] * 100)[
                                                               :4] + "% уверен. Я отослал Вам фотографию, можете проверить сами. Я думаю это также может быть: " + \
                find_translation(response[0][1]) + " или " + find_translation(response[0][2]) + " (нажмите, чтобы получить фотографию)."
            wrong_button = u"\u2620" + "Неправильно"
        else:
            r = "I think the breed of this dog is " + response[0][0] + " and I'm " + str(response[1][0] * 100)[
                                                                                     :4] + "% confident. I sent you a photo, so you can see for yourself. I also found it similar to the following breeds: " + \
                response[0][1] + ", " + response[0][2] + " (tap to get a photo)."
            wrong_button = u"\u2620" + "Wrong"

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text=response[0][1], callback_data='dog ' + response[0][1]),
                    InlineKeyboardButton(text=response[0][2], callback_data='dog ' + response[0][2]),
                    InlineKeyboardButton(text=wrong_button, callback_data='wrong'),
                ]
            ]
        )
        self.BOT.sendMessage(user.user_id, text=r, reply_markup=keyboard)

    def send_processing(self, user):
        if user.language == 'RU':
            self.BOT.sendMessage(user.user_id, "Обрабатываю изображение...")
        else:
            self.BOT.sendMessage(user.user_id, "Processing the image...")

    def send_about_menu(self, user):

        if user.language == 'RU':
            reply = 'Этот бот был разработан с использованием Python, Telepot, Django и Tensorflow. Лучше всего бот работает с чёткими изображениями без посторонних объектов. Контакты: @mshvern'
        else:
            reply = "This bot was developed using Python, Telepot, Django, and Tensorflow. This bot works best with high resolution photos that contain a single dog. Contacts: @mshvern"

        self.BOT.sendMessage(user.user_id, reply)

    def set_language(self, user, language):
        user.language = language
        user.save()
        if user.language == 'RU':
            self.BOT.sendMessage(user.user_id, "Язык изменён!")
        else:
            self.BOT.sendMessage(user.user_id, "Language set!")

    def send_photo_of_a_breed(self, user, breed):
        path = const.media_url + breed.replace(' ', '_') + '.jpg'
        if 'njrok' in const.media_url:
            self.BOT.sendMessage(user.user_id, "Take a look: " + path)
            return
        try:
            telegram_url = "https://api.telegram.org/bot" + const.bot_token + "/sendPhoto"
            response = requests.post(url=telegram_url, data={"chat_id": user.user_id, "photo": path})
            print("link: ", telegram_url, path)
            print(response.content)
            # self.BOT.sendPhoto(user.user_id, path, caption=breed)
        except Exception as e:
            pprint("Error sending a photo of a breed: " + path + str(e))
            pprint("Trying to send a link")
            try:
                self.BOT.sendMessage(user.user_id, "Take a look: " + path)
            except Exception as e:
                pprint("Can't send a file either: " + str(e))

    def wrong_result(self, user):
        if user.language == 'RU':
            response = "Спасибо за информацию! Я обязательно исправлюсь"
        else:
            response = "Thanks for telling me! I\'ll use this as an opportunity to learn"
        self.save_files(user)
        self.delete_files(user)
        self.BOT.sendMessage(user.user_id, response)

    def delete_files(self, user):
        for file in user.files.all():
            try:
                path_to_remove = file.path
                user.files.remove(file)
                os.remove(path_to_remove)
            except Exception as e:
                pprint("no file at " + file.path)

    def save_files(self, user):
        for file in user.files.all():
            try:
                copy(file.path, os.path.join(self.BASE, 'saved/' + str(user.user_id) + '_' + str(file.pk) + '.jpg'))
            except Exception as e:
                pprint("no file at " + file.path)
