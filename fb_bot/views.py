from django.views import generic
from django.http.response import HttpResponse
import json
import requests
from pprint import pprint
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from fb_bot import const
from django.utils import timezone
from AI.classify_singleton import Analyzer
import os
from urllib.parse import quote
from .models import UserLang, File
from shutil import copy


class BotView(generic.View):
	BASE = os.path.dirname(os.path.abspath(__file__))
	analyzer = Analyzer()

	@method_decorator(csrf_exempt)
	def dispatch(self, request, *args, **kwargs):
		return generic.View.dispatch(self, request, *args, **kwargs)

	def post(self, request, *args, **kwargs):
		incoming_message = json.loads(self.request.body.decode('utf-8'))
		pprint(incoming_message)
		for entry in incoming_message['entry']:
			if 'messaging' in entry:
				for message in entry['messaging']:
					if 'message' in message:
						if 'attachments' in message['message'] and message['message']['attachments'][0][
							'type'] == 'image':
							self.post_facebook_message(
								message['sender']['id'],
								"start",
								image=message['message']['attachments'][0]['payload']['url']
							)
						else:
							self.post_facebook_message(
								message['sender']['id'],
								"start"
							)
					else:
						try:
							self.post_facebook_message(
								message['sender']['id'],
								message['postback']['payload']
							)
						except KeyError:
							pprint("Unexpected value")

		return HttpResponse()

	def get(self, request, *args, **kwargs):
		if self.request.GET['hub.verify_token'] == const.verify_token:
			return HttpResponse(self.request.GET['hub.challenge'])
		else:
			return HttpResponse('Invalid Token')

	def post_facebook_message(self, fbid, postback=None, image=None):
		try:
			user = UserLang.objects.get(user_id=fbid)
		except UserLang.DoesNotExist:
			user = UserLang.objects.create(
				user_id=fbid,
			)
		if postback == 'Info':
			if user.language == 'RU':
				about_text = 'Этот бот был разработан с ипользованием Python, Django, and Tensorflow.' + \
							 ' \n\nЛучше всего бот работает с чёткими изображениями без посторонних объектов. ' + \
							 '\n\nПерейдя по ссылкам ниже, Вы можете связаться с разработчиком или использовать Telegram' + \
							 ' версию этого бота.'
			else:
				about_text = 'This bot was developed using Python, Django, and Tensorflow.' + \
							 ' \n\nThis bot works best with high resolution photos that contain a single dog. ' + \
							 '\n\nUse buttons in this message to contact the developer or view the Telegram version' + \
							 ' of this bot.'

			response_msg = json.dumps(
				{
					"recipient": {"id": fbid},
					"message":
						{
							"attachment":
								{
									"type": "template",
									"payload":
										{
											"template_type": "button",
											"text": about_text,
											"buttons":
												[
													{
														"type": "web_url",
														"title": "Telegram",
														"url": "https://t.me/breed_identifier_bot"
													},
													{
														"type": "web_url",
														"title": "Contact",
														"url": "https://t.me/mshvern"
													}
												]
										}
								}
						}
				}
			)
			return self.send_post(response_msg)
		elif postback[:4] == 'lang':
			user.language = postback[4:6]
			user.save()
			# self.post_facebook_message(fbid, 'start')
		elif postback[:3] == 'dog':
			breed_image_post = self.get_image_post(postback[3:], fbid)
			return self.send_post(breed_image_post)
		elif postback == 'wrong':
			if user.language == 'RU':
				thanks_text = 'Спасибо за информацию! Я обязательно исправлюсь'
			else:
				thanks_text = 'Thanks for telling me! I\'ll use this as an opportunity to learn'
			response_msg = json.dumps(
				{
					"recipient": {"id": fbid},
					"message":
						{
							"text": thanks_text
						}
				}
			)
			self.save_files(user)
			self.delete_files(user)
			return self.send_post(response_msg)

		if image is None:
			if user.language == 'RU':
				start_text = 'Вы можете использовать этого бота отослав ему фотографию собаки. Он обработает изображение и попытается определить породу.'
				info = 'Инфо'
				lang_change = "Смена языка"
				lang_change_load = 'langEN'
			else:
				start_text = "You can use this bot by sending a photo of a dog. It will process the image and try to identify the dog\'s breed."
				info = 'Info'
				lang_change = "Switch language"
				lang_change_load = 'langRU'
			response_msg = json.dumps(
				{
					"recipient": {"id": fbid},
					"message":
						{
							"attachment":
								{
									"type": "template",
									"payload":
										{
											"template_type": "button",
											"text": start_text,
											"buttons":
												[
													{
														"type": "postback",
														"title": info,
														"payload": "Info"
													},
													{
														"type": "postback",
														"title": lang_change,
														"payload": lang_change_load
													}
												]
										}
								}
						}
				}
			)
			self.send_post(response_msg)
		else:
			self.delete_files(user)
			imgfilename = str(timezone.now()).replace(':', '-').replace('+', '-').replace('.', '-')
			imgfilename += str(fbid) + '.jpg'
			path = os.path.join(self.BASE, imgfilename)
			with open(path, 'wb') as f:
				f.write(requests.get(image).content)

			response = self.analyzer.get_score(path)
			user.files.add(File.objects.create(path=path))
			user.save()
			if user.language == 'RU':
				r = "Я думаю это " + response[0][0] + " и я на " + str(response[1][0] * 100)[:4] + \
					"% уверен. Я отослал Вам фотографию, можете проверить сами. Я думаю это также может быть: " + \
					response[0][1] + " или " + response[0][2] + " (нажмите, чтобы получить фотографию)."
				wrong_button = 'Неправильно'
			else:
				r = "I think the breed of this dog is " + response[0][0] + " and I'm " + str(response[1][0] * 100)[:4] + \
					"% confident. I sent you a photo, so you can see for yourself. " + \
					"I also found it similar to the following breeds: " + \
					response[0][1] + ", " + response[0][2] + " (tap to get a photo)."
				wrong_button = 'Wrong'
			response_msg = self.get_image_post(response[0][0], fbid)
			pprint("Fetching from: " + const.media_url + quote(response[0][0].replace(' ', '_')) + ".jpg")
			self.send_post(response_msg)
			response_msg = json.dumps(
				{
					"recipient": {"id": fbid},
					"message":
						{
							"attachment":
								{
									"type": "template",
									"payload":
										{
											"template_type": "button",
											"text": r,
											"buttons":
												[
													{
														"type": "postback",
														"title": response[0][1],
														"payload": "dog" + response[0][1]
													},
													{
														"type": "postback",
														"title": response[0][2],
														"payload": "dog" + response[0][2]
													},
													{
														"type": "postback",
														"title": wrong_button,
														"payload": "wrong"
													}
												]
										}
								}
						}
				}
			)
			self.send_post(response_msg)

	def send_post(self, data):
		post_message_url = \
			'https://graph.facebook.com/v3.0/me/messages?access_token=' + const.access_token
		headers = {"Content-type": "application/json"}
		status = requests.post(post_message_url, headers=headers, data=data)
		pprint(status.json())
		return status.status_code

	def get_image_post(self, url, fbid):
		msg = json.dumps(
			{
				"recipient": {"id": fbid},
				"message":
					{
						"attachment":

							{
								"type": "image",
								"payload":
									{
										"url": const.media_url + quote(url.replace(' ', '_')) + ".jpg",
										"is_reusable": True
									}
							}
					}
			}
		)
		return msg

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
