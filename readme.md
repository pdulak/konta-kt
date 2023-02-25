The app works in Docker now. It can be used locally under:

`http://127.0.0.1:8314`

Or via tunnel and URL of:

`https://kontakt.dulare.com/`

Start app:

`docker-compose up`

Start tunnel:

`ssh dlr2022tunnel`

---

Work in Docker shell:

`docker exec -it konta-kt /bin/bash`

Create new app:

`python manage.py startapp new_app_name`

Once added, go to settings.py and add in INSTALLED_APPS section

---

Go to the Docker image and execute commands in Bash:

`docker exec -it <name of image> bash`

Create admin superuser:

`python manage.py createsuperuser`

Prepare migrations:

```
python manage.py makemigrations regions     # models in regions app
python manage.py makemigrations             # <- all models
```

Execute migrations:

`python manage.py migrate`
