# -* - coding: utf-8 -*-
from django import forms
from django.forms import ModelForm

from .models import Client


class ClientForm(ModelForm):
    class Meta:
        model = Client
