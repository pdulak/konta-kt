# Generated by Django 2.1.4 on 2018-12-31 10:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0011_auto_20181230_2311'),
    ]

    operations = [
        migrations.AddField(
            model_name='transactionimporttemp',
            name='is_duplicate',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
    ]
