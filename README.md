# Dogbi - Telegram Breed Identifier Bot
![Dogbi Logo](https://scontent-frt3-2.xx.fbcdn.net/v/t1.15752-9/38772043_246304856017369_1651153778415501312_n.png?_nc_cat=0&oh=610b73ec5b4b6b8c8de27610b6ddd32d&oe=5C00E6A8)
> Just [send Dogbi a message](https://t.me/breed_identifier_bot) with a photo of a dog or a person and it will analyze the image and respond with an estimate of similarity. 

* Fill out `const_empty.py` in telegram_bot directory and rename it to `const.py`</br>
* Generate a legit secret key for `settings_without_key.py` (add `SECRET_KEY = 'YOUR KEY'`) and rename it to `settings.py` </br>
* Copy the static files into AI directory (graph, breeds.csv, russian_breeds.csv should be placed in  `root/AI` directory, while static images should be placed in `root/AI/static/media/` directory)
* Build a docker image using `docker-compose build` and launch it with `docker-compose up` </br>
* Forward the `8005` and `8006` ports to a default `80` port of your server
* That's it! Dogbi is now running in a Docker on your server!
