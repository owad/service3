# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):
    dependencies = [
        ('auth', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('first_name', models.CharField(max_length=64, verbose_name='imię')),
                ('last_name', models.CharField(max_length=128, verbose_name='nazwisko')),
                ('company_name', models.CharField(max_length=128, verbose_name='firma', blank=True)),
                ('address_line1', models.CharField(max_length=128, verbose_name='adres 1', blank=True)),
                ('address_line2', models.CharField(max_length=128, verbose_name='adres 2', blank=True)),
                ('city', models.CharField(max_length=128, verbose_name='miejscowość', blank=True)),
                ('postcode', models.CharField(max_length=8, verbose_name='kod pocztowy', blank=True)),
                ('email', models.EmailField(max_length=75, verbose_name='e-mail', blank=True)),
                ('phone_number',
                 models.CharField(max_length=9, validators=[django.core.validators.RegexValidator('^(\\d{9})$')],
                                  verbose_name='telefon')),
                ('second_phone_number',
                 models.CharField(max_length=9, validators=[django.core.validators.RegexValidator('^(\\d{9})$')],
                                  verbose_name='telefon dodatkowy', blank=True)),
                ('is_subscriber', models.BooleanField(verbose_name='abonament serwisowy', default=False)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='data utworzenia')),
            ],
            options={
                'verbose_name': 'klient',
                'verbose_name_plural': 'klienci',
                'ordering': ['-created'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='User',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('auth.user',),
        ),
    ]
