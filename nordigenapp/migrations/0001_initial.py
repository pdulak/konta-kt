# Generated by Django 4.1.7 on 2023-02-27 17:55

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='NordigenTokens',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('access', models.CharField(max_length=2048)),
                ('refresh', models.CharField(max_length=2048)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('access_expiration', models.DateTimeField()),
                ('refresh_expiration', models.DateTimeField()),
            ],
        ),
    ]