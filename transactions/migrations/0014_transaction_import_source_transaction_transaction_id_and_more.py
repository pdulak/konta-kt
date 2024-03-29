# Generated by Django 4.1.7 on 2023-05-06 12:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0013_transaction_approved'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='import_source',
            field=models.CharField(blank=True, default='CSV', max_length=20),
        ),
        migrations.AddField(
            model_name='transaction',
            name='transaction_id',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='transactionimporttemp',
            name='import_source',
            field=models.CharField(blank=True, default='CSV', max_length=20),
        ),
        migrations.AddField(
            model_name='transactionimporttemp',
            name='transaction_id',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='imported_description',
            field=models.CharField(blank=True, max_length=4000, null=True),
        ),
        migrations.AlterField(
            model_name='transactionimporttemp',
            name='imported_description',
            field=models.CharField(blank=True, max_length=4000, null=True),
        ),
    ]
