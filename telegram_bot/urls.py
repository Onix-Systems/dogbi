from django.conf.urls import include, url
from .views import BotView
from telegram_bot import const

urlpatterns = [
	url(r'^' + const.bot_token + '/?$', BotView.as_view(), name='bot')
]