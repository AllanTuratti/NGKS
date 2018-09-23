# coding=utf-8

from django.shortcuts import render
from django.http import HttpResponse
from django.core.mail import send_mail
from django.conf import settings

from .forms import contato_forms


def index(request):
    return render(request, 'index.html')

def sobrenos(request):
    return render(request, 'sobrenos.html')


def contato(request):
    success = False
    form = contato_forms(request.POST or None)
    if form.is_valid():
        form.send_mail()
        success = True
    contexto = {
        'form': form,
        'success': success
    }
    return render(request, 'contato.html', contexto)

def produto(request):
    return render(request,'produto.html')

