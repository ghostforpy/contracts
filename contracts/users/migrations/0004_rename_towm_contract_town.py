# Generated by Django 4.2.11 on 2024-04-29 15:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_company_town_contract'),
    ]

    operations = [
        migrations.RenameField(
            model_name='contract',
            old_name='towm',
            new_name='town',
        ),
    ]