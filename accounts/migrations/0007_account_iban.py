# Generated by Django 4.1.7 on 2023-02-26 19:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_bank_hide'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='iban',
            field=models.CharField(blank=True, max_length=200),
        ),
    ]