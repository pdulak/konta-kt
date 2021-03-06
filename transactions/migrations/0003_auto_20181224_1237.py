# Generated by Django 2.1.4 on 2018-12-24 12:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_auto_20181224_1237'),
        ('transactions', '0002_auto_20181224_1226'),
    ]

    operations = [
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid_text', models.CharField(max_length=200)),
                ('transaction_date', models.DateField()),
                ('transaction_added', models.DateField()),
                ('amount', models.DecimalField(decimal_places=2, max_digits=12)),
                ('transaction_description', models.CharField(max_length=2000)),
                ('transaction_imported_description', models.CharField(max_length=2000)),
                ('party_name', models.CharField(max_length=500)),
                ('party_IBAN', models.CharField(max_length=200)),
                ('irrelevant', models.BooleanField(default=False)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='accounts.Account')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='transactions.Category')),
            ],
        ),
        migrations.CreateModel(
            name='TransactionType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type_name', models.CharField(max_length=200)),
            ],
        ),
        migrations.AddField(
            model_name='transaction',
            name='type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='transactions.TransactionType'),
        ),
    ]
