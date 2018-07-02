from django.conf.urls import include, url
from .views import BotView
from fb_bot import const

urlpatterns = [
	url(r'^'+const.webhook_url+'/?$', BotView.as_view(), name='bot')
]