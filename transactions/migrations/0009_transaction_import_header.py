# Generated by Django 2.1.4 on 2018-12-28 12:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('toolbox', '0002_auto_20181228_1213'),
        ('transactions', '0008_auto_20181227_2153'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='import_header',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='toolbox.ImportHeader'),
        ),
    ]
