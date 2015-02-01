# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):
    dependencies = [
        ('person', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('note', models.TextField(verbose_name='notatka')),
                ('type', models.CharField(
                    choices=[('komentarz', 'komenatrz'), ('zmiana_statusu', 'zmiana statusu'), ('sprzet', 'sprzęt')],
                    verbose_name='typ', max_length=32)),
                ('status', models.CharField(
                    choices=[('przyjety', 'przyjęty'), ('w_realizacji', 'w realizacji'), ('do_wyslania', 'do wysłania'),
                             ('w_serwisie', 'w serwisie zew.'), ('z_serwisu', 'odebrano z serwisu zew.'),
                             ('do_wydania', 'do wydania'), ('wydany', 'wydany')], max_length=32, blank=True)),
                ('hardware',
                 models.DecimalField(max_digits=10, decimal_places=2, verbose_name='koszt sprzętu', default='0.00')),
                ('software',
                 models.DecimalField(max_digits=10, decimal_places=2, verbose_name='koszt usługi', default='0.00')),
                ('transport',
                 models.DecimalField(max_digits=10, decimal_places=2, verbose_name='koszt dojazdu', default='0.00')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='data zgłoszenia')),
            ],
            options={
                'verbose_name': 'komentarz',
                'verbose_name_plural': 'komentarze',
                'ordering': ['-created'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Courier',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length='64')),
            ],
            options={
                'verbose_name': 'kurier',
                'verbose_name_plural': 'kurierzy',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('obj', models.FileField(upload_to='media_files', verbose_name='plik', blank=True)),
                ('title', models.CharField(max_length=100, verbose_name='nazwa', blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=128, verbose_name='nazwa')),
                ('producent', models.CharField(max_length=128, verbose_name='producent', blank=True)),
                ('serial', models.CharField(max_length=128, verbose_name='numer seryjny', blank=True)),
                ('invoice', models.CharField(max_length=128, verbose_name='numer faktury', blank=True)),
                ('description', models.TextField(verbose_name='opis usterki')),
                ('additional_info', models.TextField(verbose_name='informacje dodatkowe', blank=True)),
                ('status', models.CharField(
                    choices=[('przyjety', 'przyjęty'), ('w_realizacji', 'w realizacji'), ('do_wyslania', 'do wysłania'),
                             ('w_serwisie', 'w serwisie zew.'), ('z_serwisu', 'odebrano z serwisu zew.'),
                             ('do_wydania', 'do wydania'), ('wydany', 'wydany')], max_length=32)),
                ('parcel_number', models.CharField(max_length=64, verbose_name='numer przesyłki', blank=True)),
                ('external_service_name',
                 models.CharField(max_length=128, verbose_name='nazwa serwisu zewnętrznego', blank=True)),
                ('max_cost',
                 models.DecimalField(max_digits=10, decimal_places=2, verbose_name='koszt naprawy do', default='0.00')),
                ('warranty',
                 models.CharField(choices=[('N', 'Nie'), ('Y', 'Tak')], verbose_name='gwarancja', max_length=16)),
                ('courier', models.IntegerField(null=True, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='data zgłoszenia')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='ostatnia akutalizajca')),
                ('fixed_by', models.IntegerField(null=True, verbose_name='wykonane przez', blank=True)),
                ('client', models.ForeignKey(to='person.Client', verbose_name='klient')),
                ('user', models.ForeignKey(to='person.User', verbose_name='pracownik')),
            ],
            options={
                'verbose_name': 'zgłoszenie',
                'verbose_name_plural': 'zgłoszenia',
                'ordering': ['-created'],
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='file',
            name='product',
            field=models.ForeignKey(to='product.Product', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='comment',
            name='product',
            field=models.ForeignKey(to='product.Product', verbose_name='produkt'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='comment',
            name='user',
            field=models.ForeignKey(to='person.User', verbose_name='pracownik'),
            preserve_default=True,
        ),
    ]
