
from django.shortcuts import render
from django.http import HttpResponse
from django.core.mail import send_mail
from django.conf import settings
from .forms import contato_forms
from django.views.generic import View, TemplateView



class indexView(TemplateView):
    
    template_name = 'index.html'

index = indexView.as_view()

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

