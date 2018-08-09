# Dogbi - Telegram Bot that identifies the breed of a dog by a photo
![Dogbi Logo](https://scontent-frt3-2.xx.fbcdn.net/v/t1.0-9/38821307_509586642798742_7492497944529076224_n.jpg?_nc_cat=0&oh=6ac5cccea7415a7182ade58e69170a65&oe=5BF70969)
> Just [send Dogbi a message](https://t.me/breed_identifier_bot) with a photo of a dog or a person and it will analyze the image and respond with an estimate of similarity. 

* Fill out `const_empty.py` in telegram_bot directory and rename it to `const.py`</br>
* Generate a legit secret key for `settings_without_key.py` (add `SECRET_KEY = 'YOUR KEY'`) and rename it to `settings.py` </br>
* Copy the static files into AI directory (graph, breeds.csv, russian_breeds.csv should be placed in  `root/AI` directory, while static images should be placed in `root/AI/static/media/` directory)
* Build a docker image using `docker-compose build` and launch it with `docker-compose up` </br>
* Forward the `8005` and `8006` ports to a default `80` port of your server
* That's it! Dogbi is now running in a Docker on your server!
