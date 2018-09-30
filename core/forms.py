#coding=utf-8

from django import forms
from django.core.mail import send_mail
from django.conf import settings


class contato_forms(forms.Form):

    nome = forms.CharField(label='Nome')
    email = forms.EmailField(label='E-mail')
    messagem = forms.CharField(label='Mensagem', widget=forms.Textarea())

    def send_mail(self):
        nome = self.cleaned_data['nome']
        email = self.cleaned_data['email']
        messagem = self.cleaned_data['messagem']
        messagem = 'Nome: {0}\nE-mail:{1}\n{2}'.format(nome, email, messagem)
        send_mail(
            'Contato da NGKS_Shop', messagem, settings.DEFAULT_FROM_EMAIL,
            [settings.DEFAULT_FROM_EMAIL]
        )