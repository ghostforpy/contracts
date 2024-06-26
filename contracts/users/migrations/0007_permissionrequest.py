# Generated by Django 4.2.11 on 2024-05-01 09:05

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_usercontractfolders'),
    ]

    operations = [
        migrations.CreateModel(
            name='PermissionRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ada', models.BooleanField(default=False)),
                ('mpe', models.BooleanField(default=False)),
                ('mpm', models.BooleanField(default=False)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Создано')),
                ('done', models.DateTimeField(blank=True, null=True, verbose_name='Исполнено')),
                ('contract', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='permission_requests', to='users.contract', verbose_name='Контракт')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='permission_requests', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Заявка',
                'verbose_name_plural': 'Заявки',
            },
        ),
    ]
