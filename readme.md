

---

Work in Docker shell:

`docker exec -it konta-kt /bin/bash`

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
