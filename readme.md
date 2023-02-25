

---

Work in Docker shell:

`docker exec -it awshelper_awshelper_1 /bin/bash`

Create new app:

`python manage.py startapp new_app_name`

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

---

Windows:
---

Install virtualenvwrapper-win
> pip install virtualenvwrapper-win

Create a virtual environment
> mkvirtualenv konta-kt

Start working on the project:
> workon konta-kt

